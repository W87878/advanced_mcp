import React, { ButtonHTMLAttributes, ReactNode } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  loading?: boolean;
}

export function Button({ children, loading, disabled, ...props }: ButtonProps) {
  return (
    <button
      disabled={disabled || loading}
      {...props}
      className={`
        inline-flex items-center justify-center rounded-xl
        bg-gradient-to-r from-indigo-600 to-purple-600
        text-white font-semibold px-6 py-3
        shadow-lg hover:shadow-indigo-500/50 transition
        disabled:opacity-50 disabled:cursor-not-allowed
        focus:outline-none focus:ring-4 focus:ring-purple-400
        disabled:focus:ring-0
        ${props.className || ""}
      `}
    >
      {loading && (
        <svg
          className="animate-spin mr-2 h-5 w-5 text-white"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          ></circle>
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
          ></path>
        </svg>
      )}
      {children}
    </button>
  );
}
