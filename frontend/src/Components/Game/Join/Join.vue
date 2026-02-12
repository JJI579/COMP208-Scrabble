<script lang="ts" setup>
import useWebsocketStore from '@/Components/Stores/websocket';
import { onMounted } from 'vue';
import { useRoute } from 'vue-router';


const route = useRoute();



onMounted(() => {
	const websocket = useWebsocketStore()

	const code = route.query.code;

	if (code !== undefined) {
		// if not null, join game.
		console.log("joining")
		websocket.join(code as string)
	} else {

		console.log("undeifned")
	}
})

</script>



<template>


</template>


<style lang="css" scoped></style>