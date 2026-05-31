import * as React from "react";
import { cn } from "../../lib/utils";

export interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {}

const Select = React.forwardRef<HTMLSelectElement, SelectProps>(({ className, children, ...props }, ref) => {
  return (
    <select
      ref={ref}
      className={cn(
        "min-h-11 w-full rounded-xl border border-[#fdf6e3]/14 bg-[#fdf6e3]/8 px-4 py-2 text-sm text-[#fdf6e3] outline-none transition focus:border-[#ffb627] focus:ring-2 focus:ring-[#ffb627]/20",
        className
      )}
      {...props}
    >
      {children}
    </select>
  );
});
Select.displayName = "Select";

export { Select };
