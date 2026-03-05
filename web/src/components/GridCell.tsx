interface GridCellProps {
  shoveFreq: number | null;
  label: string;
  onClick?: () => void;
  isSelected?: boolean;
  size?: "sm" | "md";
}

export default function GridCell({ shoveFreq, label, onClick, isSelected, size = "md" }: GridCellProps) {
  const dim = size === "md" ? "w-9 h-9 text-[10px]" : "w-7 h-7 text-[8px]";

  const bg = shoveFreq === null
    ? "#1f2937"
    : shoveFreq === 0
    ? "#111827"
    : `linear-gradient(to right, #dc2626 ${shoveFreq * 100}%, #111827 ${shoveFreq * 100}%)`;

  return (
    <button
      onClick={onClick}
      title={shoveFreq !== null ? `${(shoveFreq * 100).toFixed(0)}% shove` : "No data"}
      style={{ background: bg }}
      className={`
        ${dim} flex items-center justify-center font-mono font-bold
        text-white border border-gray-800 rounded-sm transition-all select-none
        ${isSelected ? "ring-2 ring-yellow-400 ring-offset-1 ring-offset-gray-900 z-10 relative" : ""}
        ${onClick ? "cursor-pointer hover:brightness-125" : "cursor-default"}
      `}
    >
      {label}
    </button>
  );
}
