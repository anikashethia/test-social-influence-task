/**
 * TimelineRunner — mounts jsPsych and runs the influence task timeline.
 */

import { useEffect, useRef } from "react";
import { initJsPsych } from "jspsych";
import "jspsych/css/jspsych.css";
import { buildTimeline } from "../timeline";
import type { TaskContext } from "../timeline";

type Props = {
  ctx: TaskContext;
  onComplete: () => void;
};

export default function TimelineRunner({ ctx, onComplete }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const startedRef = useRef(false);

  useEffect(() => {
    if (!containerRef.current || startedRef.current) return;
    startedRef.current = true;

    const jsPsych = initJsPsych({
      display_element: containerRef.current,
      on_finish: () => onComplete(),
    });

    buildTimeline(ctx, jsPsych).then((timeline) => {
      jsPsych.run(timeline);
    });
  }, [ctx, onComplete]);

  return <div ref={containerRef} className="min-h-screen" />;
}
