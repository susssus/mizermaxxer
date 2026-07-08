/** Routes protected by Vercel BotID (client + server must stay in sync). */
export const BOTID_PROTECTED_ROUTES = [
  {
    path: "/api/correction",
    method: "POST",
  },
] as const;
