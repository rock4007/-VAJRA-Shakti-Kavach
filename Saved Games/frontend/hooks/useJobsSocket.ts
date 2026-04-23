"use client";

import { useEffect } from "react";

import { Job } from "../services/types";

const socketBase = (process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000").replace("http", "ws");

export function useJobsSocket(onJob: (job: Job) => void) {
  useEffect(() => {
    const ws = new WebSocket(`${socketBase}/ws/jobs`);

    ws.onopen = () => {
      ws.send("subscribe");
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        if (message?.type === "new_job" && message.payload) {
          onJob(message.payload as Job);
        }
      } catch {
        // Ignore malformed payloads from any transient backend issue.
      }
    };

    return () => {
      ws.close();
    };
  }, [onJob]);
}
