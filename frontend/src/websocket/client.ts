import type { WebSocketMessage } from "../types";

const WS_BASE_URL = (import.meta.env.VITE_WS_BASE_URL as string | undefined) ?? "ws://localhost:8000";

type MessageHandler = (message: WebSocketMessage) => void;
type StatusChangeHandler = (connected: boolean) => void;

export class WebSocketClient {
  private socket: WebSocket | null = null;
  private onMessage: MessageHandler | null = null;
  private onStatusChange: StatusChangeHandler | null = null;

  get isConnected(): boolean {
    return this.socket?.readyState === WebSocket.OPEN;
  }

  connect(
    onMessage: MessageHandler,
    onStatusChange: StatusChangeHandler,
  ): void {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) return;

    this.onMessage = onMessage;
    this.onStatusChange = onStatusChange;

    this.socket = new WebSocket(`${WS_BASE_URL}/ws/stream`);

    this.socket.onopen = () => {
      this.onStatusChange?.(true);
    };

    this.socket.onmessage = (event: MessageEvent) => {
      try {
        const parsed = JSON.parse(event.data as string) as WebSocketMessage;
        this.onMessage?.(parsed);
      } catch (e) {
        // Malformed server messages are logged and dropped — never crash the connection
        console.warn("[WebSocketClient] Received unparseable message:", e);
      }
    };

    this.socket.onclose = () => {
      this.onStatusChange?.(false);
    };

    this.socket.onerror = () => {
      this.onStatusChange?.(false);
    };
  }

  disconnect(): void {
    this.socket?.close();
    this.socket = null;
  }
}
