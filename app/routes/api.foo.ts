import type { Route } from "./+types/api.foo";

// GET /api/foo
export async function loader(_: Route.LoaderArgs) {
  return Response.json({
    bar: true,
    serverTime: new Date().toISOString(),
    uptimeSeconds: Math.round(process.uptime()),
  });
}
