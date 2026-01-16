import { createApp } from "vue";
import ToolboxPage from "./toolbox-page.vue";
import "@/styles/ecommerce-image.css";
import { requireSession } from "@/shared/supabase";

async function bootstrap() {
  await requireSession();
  createApp(ToolboxPage).mount("#app");
}

void bootstrap();
