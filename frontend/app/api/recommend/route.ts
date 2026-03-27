import { NextResponse } from "next/server";

const API_BASE_URL =
  process.env.API_BASE_URL ??
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  "https://librorank.onrender.com";

export async function GET() {
  try {
    const upstream = await fetch(`${API_BASE_URL}/recommend`, {
      method: "GET",
      cache: "no-store"
    });

    const text = await upstream.text();
    const contentType = upstream.headers.get("content-type") ?? "application/json";

    return new NextResponse(text, {
      status: upstream.status,
      headers: { "content-type": contentType }
    });
  } catch {
    return NextResponse.json(
      { detail: "Unable to reach LibroRank API from frontend server." },
      { status: 502 }
    );
  }
}
