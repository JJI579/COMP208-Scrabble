import { defineStore } from "pinia";
import type { Item} from "@/types";
 
export const useShopStore = defineStore("shop", {
    state: () => ({
        items: [] as Item[],
        nameStyle: "",
        profileStyle: "",
        badge: ""
    }),
    actions: {
        setItems(items: Item[]) {
            this.items = items;
            this.applyEquipped(items);
        },

        applyEquipped(items: Item[]) {
            this.nameStyle = ""
            this.profileStyle = ""
            this.badge = ""

            for (const item of items) {
                if (!item.equipped) continue;

                if (item.category === "name_style") {
                    this.nameStyle = item.effect
                }

                if (item.category === "profile_border") {
                    this.profileStyle = item.effect
                }

                if (item.category === "badge") {
                    this.badge = item.effect
                }
            }
        },

        equipItem(id: number) {
            const item = this.items.find(i => i.itemID === id);
            if (!item) {
                return;
            }

            item.equipped = true;
            this.applyEquipped(this.items);
        },

        unequipItem(id: number) {
            const item = this.items.find(i => i.itemID === id);
            if (!item) {
                return;
            }

            item.equipped = false;
            this.applyEquipped(this.items);
        }
    }
});