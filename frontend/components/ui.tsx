import type { ReactNode } from "react";

// Green rounded-bottom page header (compact).
export function PageHeader({
  title,
  subtitle,
  greeting,
}: {
  title: string;
  subtitle?: string;
  greeting?: string;
}) {
  return (
    <div className="phead">
      <div className="phead-main">
        {greeting && <div className="phead-hi">{greeting}</div>}
        {greeting ? <div className="phead-name">{title}</div> : <h1>{title}</h1>}
        {subtitle && <p>{subtitle}</p>}
      </div>
    </div>
  );
}

export function Kpi({
  icon,
  value,
  unit,
  label,
  trend,
  flat,
}: {
  icon: ReactNode;
  value: ReactNode;
  unit?: string;
  label: string;
  trend?: string;
  flat?: boolean;
}) {
  return (
    <div className="kpi">
      <span className="kpi-ico">{icon}</span>
      <div className="kpi-body">
        <div className="kpi-label">{label}</div>
        <div className="kpi-value">
          {unit && <span className="unit">{unit}</span>}
          {unit ? " " : null}
          {value}
        </div>
      </div>
      {trend && <span className={`kpi-trend${flat ? " flat" : ""}`}>{trend}</span>}
    </div>
  );
}
