// src/components/ui/textarea.tsx
import React, { forwardRef } from "react";

export const Textarea = forwardRef<HTMLTextAreaElement, React.TextareaHTMLAttributes<HTMLTextAreaElement>>(
  ({ className, ...props }, ref) => (
    <textarea
      ref={ref}
      className={"resize-none border rounded-md p-3 " + (className || "")}
      {...props}
    />
  )
);

Textarea.displayName = "Textarea";
