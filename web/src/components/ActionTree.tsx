"use client";

import { POSITION_NAMES } from "@/lib/ranges";

interface ActionTreeProps {
  history: string;
  onAction: (action: "S" | "F") => void;
  onBack: () => void;
}

export default function ActionTree({ history, onAction, onBack }: ActionTreeProps) {
  const isTerminal = history.length === 4;
  const currentPos = POSITION_NAMES[history.length] ?? "—";
  const facingShove = history.includes("S");

  const crumbs = history.split("").map((action, i) => ({
    position: POSITION_NAMES[i],
    label: action === "S"
      ? (history.slice(0, i).includes("S") ? "Call" : "Shove")
      : "Fold",
    isShove: action === "S",
  }));

  return (
    <div className="flex flex-col gap-4">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm flex-wrap min-h-[28px]">
        <span className="text-gray-500 font-mono">Start</span>
        {crumbs.map((c, i) => (
          <span key={i} className="flex items-center gap-2">
            <span className="text-gray-600">→</span>
            <span className="font-mono text-gray-400">{c.position}</span>
            <span className={`px-2 py-0.5 rounded text-xs font-semibold ${
              c.isShove ? "bg-red-900 text-red-200" : "bg-gray-700 text-gray-400"
            }`}>
              {c.label}
            </span>
          </span>
        ))}
        {!isTerminal && (
          <span className="flex items-center gap-2">
            <span className="text-gray-600">→</span>
            <span className="font-mono text-yellow-400 font-bold">{currentPos}</span>
          </span>
        )}
      </div>

      {/* Buttons */}
      {!isTerminal ? (
        <div className="flex gap-3 items-center">
          <button
            onClick={() => onAction("S")}
            className="px-5 py-2 rounded font-semibold text-white bg-red-700 hover:bg-red-600 transition-colors"
          >
            {facingShove ? "Call" : "Shove"}
          </button>
          <button
            onClick={() => onAction("F")}
            className="px-5 py-2 rounded font-semibold text-white bg-gray-700 hover:bg-gray-600 transition-colors"
          >
            Fold
          </button>
          {history.length > 0 && (
            <button
              onClick={onBack}
              className="px-4 py-2 rounded text-gray-400 border border-gray-600 hover:border-gray-400 transition-colors text-sm"
            >
              ← Back
            </button>
          )}
        </div>
      ) : (
        <div className="flex items-center gap-3">
          <span className="text-gray-500 text-sm italic">All players have acted</span>
          <button
            onClick={onBack}
            className="px-4 py-2 rounded text-gray-400 border border-gray-600 hover:border-gray-400 transition-colors text-sm"
          >
            ← Back
          </button>
        </div>
      )}
    </div>
  );
}
