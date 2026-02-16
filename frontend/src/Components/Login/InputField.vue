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
  width: 100%;
  position: relative;
}

.input__field {
  font-size: 1rem;
  padding: 0.9em 0.8em;
  width: 100%;
  height: 3.2rem;
  border-radius: 10px;
  border: 1px solid rgba(73, 11, 11, 0);
  background: rgba(255,255,255,0.08);
  color: white;
  outline: none;
  transition: 0.2s;
}

.input__field:focus {
  border: 1px solid #7b86ff;
  box-shadow: 0 0 10px rgba(123,134,255,0.4);
}

.input--error {
  border: 1px solid red;
}

.text {
  position: absolute;
  top: 50%;
  left: 5%;
  transform: translateY(-60%);
  font-size: small;
  color: #1c1c1d;
  transition: 0.3s ease all;
  pointer-events: none;
}

.text--error {
  color: red;
}

.text--active {
  font-size: 0.7rem;
  top: 15%;
  left: 4%;
}

</style>