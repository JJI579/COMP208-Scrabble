<script lang="ts" setup>
import { ref, type PropType, type Ref } from 'vue';


const props = defineProps({
	placeholder: {
		required: true,
		type: String
	},
	type: {
		required: false,
		default: "text",
		type: String
	},
	showError: {
		required: false,
		default: false,
		type: Boolean
	}
})


const isActive = ref(false);
const model = defineModel<string>('input')
</script>



<template>

	<div class="input">
		<input class="input__field" v-model="model" @focus="isActive = true" @blur="isActive = false"
			:class="{ 'input--error': props.showError && (model ?? '').length == 0 }" :type="props.type">
		<div class="text"
			:class="{ 'text--active': isActive || (model ?? '').length > 0, 'text--error': props.showError && (model ?? '').length == 0 }">
			{{ props.placeholder }}
		</div>
	</div>

</template>


<style lang="css" scoped>
.input {
	width: 80%;
	position: relative;
}

.input__field {
	font-size: 1rem;
	padding: 0.6em 0.8em;
	width: 100%;
	height: 3.5rem;
	border-radius: 8px;

}

.input--error {
	border: 1px solid red;
}

.text {
	position: absolute;
	top: 50%;
	left: 5%;
	transform: translateY(-75%);
	font-size: small;
	color: grey;
	transition: 0.5s ease all;
}

.text--error {
	color: red;
}

.text--active {
	font-size: smaller;
	top: 25%;
	left: 4%;
}
</style>