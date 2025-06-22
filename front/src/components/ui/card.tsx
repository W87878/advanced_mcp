import React, { ReactNode } from "react";

interface CardProps {
  children: ReactNode;
  className?: string;
}

interface CardContentProps {
  children: ReactNode;
  className?: string;
}

export function Card({ children, className }: CardProps) {
  return (
    <div
      className={`
        bg-white rounded-2xl shadow-2xl border border-gray-200
        ${className || ""}
      `}
    >
      {children}
    </div>
  );
}

export function CardContent({ children, className }: CardContentProps) {
  return <div className={`p-6 text-gray-900 leading-relaxed ${className || ""}`}>{children}</div>;
}
