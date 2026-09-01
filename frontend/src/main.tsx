import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { RealtimeClassroom } from "./features/lesson/RealtimeClassroom";
import "./styles.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode><RealtimeClassroom channel="lesson_demo" uid={Math.floor(Math.random() * 1_000_000) + 1} /></StrictMode>,
);

