import React from "react";

type Props = {
  steps: string[];
  current: number;
  next: number;
};

export function Stepper({ steps, current, next }: Props) {
  return (
    <div className="stepper">
      {steps.map((s, i) => (
        <div className={`step ${i <= current ? "active" : ""} ${i === current ? "current" : ""} ${i === next ? "next" : ""}`} key={s}>
          <span>{i + 1}</span>
          <label>{s}</label>
          {i === current && <small>Current</small>}
          {i === next && <small>Next</small>}
        </div>
      ))}
    </div>
  );
}
