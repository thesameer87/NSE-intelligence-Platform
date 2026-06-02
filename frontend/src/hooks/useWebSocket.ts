import { useState, useEffect, useRef } from "react";
import { WebSocketClient } from "../websocket/client";
import type { WebSocketMessage } from "../types";

interface UseWebSocketResult {
  isConnected: boolean;
  lastMessage: WebSocketMessage | null;
}

export function useWebSocket(): UseWebSocketResult {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const clientRef = useRef<WebSocketClient | null>(null);

  useEffect(() => {
    const client = new WebSocketClient();
    clientRef.current = client;

    client.connect(
      (message) => setLastMessage(message),
      (connected) => setIsConnected(connected),
    );

    return () => {
      client.disconnect();
    };
  }, []);

  return { isConnected, lastMessage };
}
