"use client";

import { useState, useRef, forwardRef, useImperativeHandle, useEffect } from "react";
import { Send, Bot, User, Loader2 } from "lucide-react";

export interface OrchestrateChatEmbedHandle {
  tryAutoFill: (text: string) => boolean;
}

interface OrchestrateChatEmbedProps {
  onReady?: () => void;
}

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

// Mock AEGIS responses based on incident content
function getAegisResponse(input: string): string {
  const lowerInput = input.toLowerCase();

  if (lowerInput.includes("p1") || lowerInput.includes("critical")) {
    return `**AEGIS Triage Analysis**

**Severity:** Critical (P1)
**Recommended Action:** Immediate escalation required

**Analysis:**
- High-impact incident detected
- Initiating automated runbook: "Critical Incident Response"
- Notifying on-call SRE team
- Creating war room channel

**Next Steps:**
1. Automated health checks initiated
2. Service dependencies being analyzed
3. Rollback options being evaluated

*Estimated resolution: Escalated to L2 support*`;
  }

  if (lowerInput.includes("timeout") || lowerInput.includes("latency")) {
    return `**AEGIS Triage Analysis**

**Issue Type:** Performance/Timeout
**Confidence:** 94%

**Root Cause Analysis:**
- Potential database connection pool exhaustion
- Network latency spike detected in region eu-west-1
- Similar pattern to INC-2024-001 (resolved)

**Automated Actions:**
1. ✅ Connection pool size increased (50 → 100)
2. ✅ Circuit breaker threshold adjusted
3. ⏳ Monitoring for improvement...

**Status:** Auto-remediation in progress`;
  }

  if (lowerInput.includes("auth") || lowerInput.includes("jwt") || lowerInput.includes("token")) {
    return `**AEGIS Triage Analysis**

**Issue Type:** Authentication/Authorization
**Confidence:** 91%

**Diagnosis:**
- JWT signing key rotation may be required
- Token validation cache potentially stale
- OAuth provider connectivity: OK

**Automated Actions:**
1. ✅ JWT signing keys refreshed
2. ✅ Token cache cleared
3. ✅ Auth service pods restarted (2/2)

**Status:** Auto-resolved - monitoring for 15 minutes`;
  }

  if (lowerInput.includes("kafka") || lowerInput.includes("consumer") || lowerInput.includes("lag")) {
    return `**AEGIS Triage Analysis**

**Issue Type:** Message Queue Backlog
**Confidence:** 88%

**Diagnosis:**
- Consumer lag detected: 45,000 messages
- Consumer group: payment-processor
- Partition rebalance in progress

**Recommendation:**
- Scale consumer instances from 3 → 6
- Consider increasing partition count

**Action Required:** Manual approval needed for scaling
*Escalating to L2 for capacity decision*`;
  }

  return `**AEGIS Triage Analysis**

**Incident Received**
Processing incident details...

**Initial Assessment:**
- Incident logged and categorized
- Checking against known issue patterns
- Analyzing service dependencies

**Automated Checks:**
1. ✅ Service health verified
2. ✅ Recent deployments checked
3. ✅ Related alerts correlated

**Recommendation:** Monitoring situation. Will escalate if metrics deteriorate.

*Type additional details for deeper analysis.*`;
}

export const OrchestrateChatEmbed = forwardRef<OrchestrateChatEmbedHandle, OrchestrateChatEmbedProps>(
  function OrchestrateChatEmbed({ onReady }, ref) {
    const [messages, setMessages] = useState<Message[]>([
      {
        id: "welcome",
        role: "assistant",
        content: "Hello! I'm **AEGIS**, your AI-powered incident triage assistant. Paste an incident or describe an issue, and I'll help analyze and recommend actions.",
        timestamp: new Date(),
      },
    ]);
    const [input, setInput] = useState("");
    const [isTyping, setIsTyping] = useState(false);
    const inputRef = useRef<HTMLTextAreaElement>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Expose tryAutoFill method to parent
    useImperativeHandle(ref, () => ({
      tryAutoFill: (text: string): boolean => {
        setInput(text);
        inputRef.current?.focus();
        return true;
      },
    }));

    useEffect(() => {
      onReady?.();
    }, [onReady]);

    useEffect(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const handleSend = async () => {
      if (!input.trim() || isTyping) return;

      const userMessage: Message = {
        id: Date.now().toString(),
        role: "user",
        content: input.trim(),
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setInput("");
      setIsTyping(true);

      // Simulate AI processing delay
      await new Promise((resolve) => setTimeout(resolve, 1500 + Math.random() * 1000));

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: getAegisResponse(userMessage.content),
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setIsTyping(false);
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }
    };

    return (
      <div className="flex flex-col h-[450px] border rounded-lg bg-background shadow-lg overflow-hidden">
        {/* Header */}
        <div className="flex items-center gap-2 px-4 py-3 bg-primary text-primary-foreground border-b">
          <Bot className="h-5 w-5" />
          <span className="font-medium">AEGIS Triage Agent</span>
          <span className="ml-auto text-xs opacity-80">watsonx Orchestrate</span>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex gap-3 ${message.role === "user" ? "flex-row-reverse" : ""}`}
            >
              <div
                className={`flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center ${
                  message.role === "user"
                    ? "bg-primary text-primary-foreground"
                    : "bg-blue-600 text-white"
                }`}
              >
                {message.role === "user" ? (
                  <User className="h-4 w-4" />
                ) : (
                  <Bot className="h-4 w-4" />
                )}
              </div>
              <div
                className={`max-w-[80%] rounded-lg px-4 py-2 text-sm ${
                  message.role === "user"
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted"
                }`}
              >
                <div className="whitespace-pre-wrap prose prose-sm dark:prose-invert max-w-none">
                  {message.content.split("\n").map((line, i) => {
                    if (line.startsWith("**") && line.endsWith("**")) {
                      return <strong key={i} className="block">{line.replace(/\*\*/g, "")}</strong>;
                    }
                    if (line.startsWith("- ") || line.startsWith("1. ") || line.startsWith("2. ") || line.startsWith("3. ")) {
                      return <div key={i} className="ml-2">{line}</div>;
                    }
                    if (line.startsWith("*") && line.endsWith("*")) {
                      return <em key={i} className="block text-muted-foreground">{line.replace(/\*/g, "")}</em>;
                    }
                    return <span key={i}>{line}<br /></span>;
                  })}
                </div>
              </div>
            </div>
          ))}
          {isTyping && (
            <div className="flex gap-3">
              <div className="flex-shrink-0 h-8 w-8 rounded-full bg-blue-600 text-white flex items-center justify-center">
                <Bot className="h-4 w-4" />
              </div>
              <div className="bg-muted rounded-lg px-4 py-2">
                <Loader2 className="h-4 w-4 animate-spin" />
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="border-t p-3">
          <div className="flex gap-2">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Paste incident or describe issue..."
              className="flex-1 resize-none rounded-lg border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              rows={2}
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || isTyping}
              className="px-4 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    );
  }
);
