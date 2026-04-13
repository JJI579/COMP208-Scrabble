import Logger from "@/logging/Logger";
import { defineStore } from "pinia";
import { ref } from "vue";

type AlertData = {
    text: string,
    type: string,
    persistent?: boolean
}

const alertLog = new Logger("alert");

const useAlertStore = defineStore("alert", () => {
	const isActive = ref(false);
    const alerts = ref<AlertData[]>([]);
    const currentAlert = ref<AlertData | null>(null);
    const ALERT_DURATION = 2500;


    function alert(alertData: AlertData | null) {
        if (isActive.value === true) {
            if (alertData !== null) {
                alerts.value.push(alertData)
                alertLog.info("Appended item to queue, already active")
            }
        } else {
            const data = alerts.value.shift()
            if (data === undefined) {
                if (alertData !== null) {
                    currentAlert.value = alertData
                    alertLog.info("Set current alert to parameter, no queue.")
                } else {
                    alertLog.info("Deactivated alert")
                    return;
                }
            } else {
                currentAlert.value = data
                alertLog.info("Set current alert to first item in queue")
            }
            isActive.value = true
            alertLog.info("Activated alert")
            if(!currentAlert.value?.persistent) {
                setTimeout(() => {
                    isActive.value = false
                    alert(null)
                }, ALERT_DURATION);
            }
        }
    }
    
    function dismiss(){
        isActive.value = false;
        setTimeout(() => {
            alert(null)
        }, 200);
    }

	return { isActive, alert, currentAlert, dismiss };
})

alertLog.debug("Alert store initialized");

export default useAlertStore;