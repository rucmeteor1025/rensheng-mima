import * as React from "react";
import { cn } from "../../lib/utils";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {}

const Input = React.forwardRef<HTMLInputElement, InputProps>(({ className, type, ...props }, ref) => {
  return (
    <input
      type={type}
      className={cn(
        "flex min-h-11 w-full rounded-xl border border-[#fdf6e3]/14 bg-[#fdf6e3]/8 px-4 py-2 text-sm text-[#fdf6e3] outline-none transition focus:border-[#ffb627] focus:ring-2 focus:ring-[#ffb627]/20 placeholder:text-[#fdf6e3]/35",
        className
      )}
      ref={ref}
      {...props}
    />
  );
});
Input.displayName = "Input";

export { Input };
