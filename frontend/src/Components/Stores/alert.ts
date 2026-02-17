import { defineStore } from "pinia";
import { ref } from "vue";

type AlertData = {
    text: string,
    type: string
}

const useAlertStore = defineStore("alert", () => {
	const isActive = ref(false);
    const alerts = ref<AlertData[]>([]);
    const currentAlert = ref<AlertData | null>(null);
    const ALERT_DURATION = 5000;


    function alert(alertData: AlertData | null) {
        if (isActive.value === true) {
            if (alertData !== null) {
                alerts.value.push(alertData)
            }
        } else {
            const data = alerts.value.shift()
            if (data === undefined) {
                if (alertData !== null) {
                    currentAlert.value = alertData
                    console.log("Active store - set to parameter provided")
                } else {
                    // exit...?
                    return;
                }
            } else {
                currentAlert.value = data
                console.log("Active store - set to first item in array")
            }
            isActive.value = true
            console.log("Active store - activated")
            setTimeout(() => {
                isActive.value = false
                alert(null)
            }, ALERT_DURATION);
        }
    }

	return { isActive, alert, currentAlert };
})

export default useAlertStore;
