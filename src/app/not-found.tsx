import Link from "next/link";
import { SiteFooter } from "@/components/site-footer";

export default function NotFound() {
  return (
    <>
    <main className="container" style={{ padding: "120px 0 160px" }}>
      <p
        className="mono"
        style={{ marginBottom: 16, color: "var(--ink-mute)" }}
      >
        404
      </p>
      <h1
        style={{
          fontFamily: "var(--serif)",
          fontSize: "clamp(2rem, 5vw, 3.5rem)",
          lineHeight: 1.1,
          marginBottom: 16,
        }}
      >
        This page doesn&rsquo;t exist yet.
      </h1>
      <p style={{ maxWidth: 480, marginBottom: 32, color: "var(--ink-mute)" }}>
        The guide you&rsquo;re looking for may still be in the works. Head back
        to the homepage or read our latest field report.
      </p>
      <div style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>
        <Link href="/" className="home-hero-btn">
          Back to home →
        </Link>
        <Link href="/articles/sendero-los-quetzales" className="cat-section-link">
          Read the Quetzal Trail guide →
        </Link>
      </div>
    </main>
    <SiteFooter locale="en" />
    </>
  );
}
