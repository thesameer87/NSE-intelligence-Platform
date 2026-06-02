import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { WebSocketClient } from "../websocket/client";

// WebSocket mock — must be a class (constructor) for `new WebSocket(...)` to work
let mockWsInstance: MockWebSocket;

class MockWebSocket {
  static readonly OPEN = 1;
  readyState = 0; // starts as CONNECTING — so isConnected is initially false
  onopen: (() => void) | null = null;
  onmessage: ((event: { data: string }) => void) | null = null;
  onclose: (() => void) | null = null;
  onerror: (() => void) | null = null;
  close = vi.fn(() => {
    this.readyState = 3;
    this.onclose?.();
  });

  constructor() {
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    mockWsInstance = this;
  }

  triggerOpen() {
    this.readyState = MockWebSocket.OPEN;
    this.onopen?.();
  }
  triggerMessage(data: string) {
    this.onmessage?.({ data });
  }
  triggerClose() {
    this.readyState = 3;
    this.onclose?.();
  }
  triggerError() {
    this.onerror?.();
  }
}

vi.stubGlobal("WebSocket", MockWebSocket);

describe("WebSocketClient", () => {
  let client: WebSocketClient;

  beforeEach(() => {
    client = new WebSocketClient();
  });

  afterEach(() => {
    client.disconnect();
  });

  it("reports disconnected before connect is called", () => {
    expect(client.isConnected).toBe(false);
  });

  it("calls onStatusChange(true) when socket opens", () => {
    const onStatusChange = vi.fn();
    client.connect(vi.fn(), onStatusChange);
    mockWsInstance.triggerOpen();
    expect(onStatusChange).toHaveBeenCalledWith(true);
  });

  it("calls onMessage with parsed payload", () => {
    const onMessage = vi.fn();
    client.connect(onMessage, vi.fn());
    mockWsInstance.triggerOpen();
    mockWsInstance.triggerMessage(
      JSON.stringify({ event: "system_status", data: { status: "ok" } }),
    );
    expect(onMessage).toHaveBeenCalledWith({
      event: "system_status",
      data: { status: "ok" },
    });
  });

  it("silently drops malformed messages", () => {
    const onMessage = vi.fn();
    client.connect(onMessage, vi.fn());
    mockWsInstance.triggerOpen();
    mockWsInstance.triggerMessage("not-json{{");
    expect(onMessage).not.toHaveBeenCalled();
  });

  it("calls onStatusChange(false) on socket close", () => {
    const onStatusChange = vi.fn();
    client.connect(vi.fn(), onStatusChange);
    mockWsInstance.triggerClose();
    expect(onStatusChange).toHaveBeenCalledWith(false);
  });

  it("calls onStatusChange(false) on socket error", () => {
    const onStatusChange = vi.fn();
    client.connect(vi.fn(), onStatusChange);
    mockWsInstance.triggerError();
    expect(onStatusChange).toHaveBeenCalledWith(false);
  });

  it("disconnect closes the socket", () => {
    client.connect(vi.fn(), vi.fn());
    client.disconnect();
    expect(mockWsInstance.close).toHaveBeenCalled();
  });
});
