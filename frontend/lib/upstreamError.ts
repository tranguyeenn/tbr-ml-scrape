import { NextResponse } from "next/server";

/** Use when fetch() to FastAPI throws (connection refused, etc.). */
export function upstreamUnreachableResponse(): NextResponse {
  return NextResponse.json({ detail: "Service unavailable." }, { status: 502 });
}
