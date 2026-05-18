"use client";

import { useState } from "react";

export function NewsletterForm() {
  const [submitted, setSubmitted] = useState(false);
  return (
    <form
      className="nl-form"
      onSubmit={(e) => {
        e.preventDefault();
        setSubmitted(true);
      }}
    >
      <input
        type="email"
        placeholder="your@email.com"
        required
        aria-label="Email"
      />
      <button type="submit">{submitted ? "Thanks ✓" : "Subscribe"}</button>
    </form>
  );
}
