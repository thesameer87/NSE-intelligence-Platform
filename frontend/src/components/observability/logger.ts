/**
 * Deterministic console-safe reporting boundary.
 * In V1, this writes safely to the console.
 * In V2, this will be wired to Sentry/Datadog or similar without changing the call sites.
 */

type LogLevel = "debug" | "info" | "warn" | "error";

interface LogPayload {
  message: string;
  context?: Record<string, unknown>;
  error?: Error;
}

class FrontendLogger {
  private formatMessage(level: LogLevel, payload: LogPayload): string {
    const timestamp = new Date().toISOString();
    return `[${timestamp}] [${level.toUpperCase()}] ${payload.message}`;
  }

  debug(message: string, context?: Record<string, unknown>) {
     
    console.debug(this.formatMessage("debug", { message, context }), context ?? "");
  }

  info(message: string, context?: Record<string, unknown>) {
     
    console.info(this.formatMessage("info", { message, context }), context ?? "");
  }

  warn(message: string, context?: Record<string, unknown>) {
     
    console.warn(this.formatMessage("warn", { message, context }), context ?? "");
  }

  error(message: string, error?: Error, context?: Record<string, unknown>) {
     
    console.error(this.formatMessage("error", { message, context, error }), error, context ?? "");
  }
}

export const logger = new FrontendLogger();
