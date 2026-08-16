"use client";

import { usePreview } from "./PreviewProvider";

export default function PreviewBanner() {
  const { previewMode, customerName, exitPreview } = usePreview();

  if (!previewMode) return null;

  return (
    <div className="w-full bg-yellow-500 text-black px-4 py-2 text-sm flex items-center justify-between">
      <div>
        <strong>Preview mode</strong> — viewing as {customerName ?? "customer"}. No admin actions available.
      </div>
      <div>
        <button className="ml-4 text-xs underline" onClick={() => exitPreview()}>
          Exit preview
        </button>
      </div>
    </div>
  );
}
