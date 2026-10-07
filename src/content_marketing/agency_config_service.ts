import { join } from "path";
import { existsSync, readFileSync, readdirSync } from "fs";

export interface AgencyBrand {
  primary_color: string;
  primary_hover: string;
  secondary_prestige: string;
  background_sand: string;
  card_bg: string;
  accent_warm_brown: string;
  accent_deep_brown: string;
  text_main: string;
  text_muted: string;
  font_heading: string;
  font_body: string;
  logo_main: string;
  logo_round: string;
  logo_badge: string;
}

export interface AgencyPersona {
  name: string;
  role: string;
  editorial_angle: string;
  signature_topics: string[];
}

export interface AgencyProfile {
  agency_id: string;
  name: string;
  short_name: string;
  tagline: string;
  brand: AgencyBrand;
  territory: {
    region_name: string;
    focus_communes: string[];
    default_commune: string;
  };
  personas: AgencyPersona[];
  competitors_monitored: Array<{ name: string; type: string; focus: string }>;
  telemetry_settings: {
    ga4_measurement_id: string;
    gsc_property: string;
    meta_pixel_id: string;
    linkedin_insight_tag: string;
  };
}

export class AgencyConfigService {
  private profilesDir: string;

  constructor(baseDir?: string) {
    const root = baseDir || process.cwd();
    this.profilesDir = join(root, "src", "config", "agency_profiles");
  }

  public getProfile(agencyId: string = "desormiere_vanhalst"): AgencyProfile {
    const filePath = join(this.profilesDir, `${agencyId}.json`);
    if (existsSync(filePath)) {
      try {
        return JSON.parse(readFileSync(filePath, "utf-8")) as AgencyProfile;
      } catch (err) {
        console.error(`[AgencyConfigService] Error reading profile ${agencyId}:`, err);
      }
    }

    // Fallback to D&V default
    const dvPath = join(this.profilesDir, "desormiere_vanhalst.json");
    if (existsSync(dvPath)) {
      return JSON.parse(readFileSync(dvPath, "utf-8")) as AgencyProfile;
    }

    throw new Error(`[AgencyConfigService] No valid profile found for agency ${agencyId}`);
  }

  public listProfiles(): Array<{ agency_id: string; name: string; region: string }> {
    if (!existsSync(this.profilesDir)) return [];
    const files = readdirSync(this.profilesDir).filter(f => f.endsWith(".json"));
    return files.map(f => {
      try {
        const data = JSON.parse(readFileSync(join(this.profilesDir, f), "utf-8"));
        return {
          agency_id: data.agency_id || f.replace(".json", ""),
          name: data.name || "Agence Inconnue",
          region: data.territory?.region_name || "Genève"
        };
      } catch {
        return { agency_id: f.replace(".json", ""), name: f, region: "Genève" };
      }
    });
  }
}
