import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "../../lib/utils";

const buttonVariants = cva(
  "inline-flex min-h-11 items-center justify-center gap-2 rounded-full px-5 text-sm font-bold transition-[background,color,border,transform] duration-[400ms] ease-[cubic-bezier(0.25,1,0.5,1)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#ffb627] disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "border border-[#ffb627] bg-[#ffb627] text-[#050401] hover:bg-[#fdf6e3] hover:border-[#fdf6e3]",
        outline: "border border-[#fdf6e3]/25 bg-transparent text-[#fdf6e3] hover:bg-[#fdf6e3] hover:text-[#050401]",
        ghost: "bg-transparent text-[#fdf6e3]/80 hover:bg-[#fdf6e3]/10 hover:text-[#fdf6e3]",
        danger: "border border-[#bc4749] bg-[#bc4749] text-[#fdf6e3] hover:bg-[#fdf6e3] hover:text-[#050401]"
      },
      size: {
        default: "h-11",
        lg: "h-13 px-7 text-base",
        icon: "h-11 w-11 px-0"
      }
    },
    defaultVariants: {
      variant: "default",
      size: "default"
    }
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const classes = cn(buttonVariants({ variant, size, className }));
    if (asChild && React.isValidElement<{ className?: string }>(props.children)) {
      return React.cloneElement(props.children, {
        className: cn(classes, props.children.props.className)
      });
    }
    return <button className={classes} ref={ref} {...props} />;
  }
);
Button.displayName = "Button";

export { Button, buttonVariants };
