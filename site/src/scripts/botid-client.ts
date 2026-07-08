import { initBotId } from "botid/client/core";
import { BOTID_PROTECTED_ROUTES } from "../lib/botid";

initBotId({
  protect: [...BOTID_PROTECTED_ROUTES],
});
