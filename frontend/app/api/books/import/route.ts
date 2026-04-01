import { NextRequest, NextResponse } from "next/server";

import { backendBaseUrl } from "../../../../lib/backendUrl";
import { upstreamUnreachableResponse } from "../../../../lib/upstreamError";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const upstream = await fetch(`${backendBaseUrl()}/books/import`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(body),
      cache: "no-store"
    });

    const text = await upstream.text();
    const contentType = upstream.headers.get("content-type") ?? "application/json";
    return new NextResponse(text, {
      status: upstream.status,
      headers: { "content-type": contentType }
    });
  } catch {
    return upstreamUnreachableResponse();
  }
}
