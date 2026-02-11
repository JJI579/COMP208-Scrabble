<script lang="ts" setup>

const props = defineProps({
	location: {
		type: String,
		required: true
	},
	name: {
		type: String,
		required: true
	},
	icon: {
		type: String,
		required: true
	}
});

</script>



<template>

	<RouterLink :to="{ name: props.location }" class="link">
		<div class="menu__option">
			<div class="icon">
				<i class="pi" :class="props.icon"></i>
			</div>
			<div class="title">
				{{ props.name }}
			</div>
		</div>
	</RouterLink>
</template>


<style lang="css" scoped>
.link {
	color: inherit;
	text-decoration: none;
}

.menu__option {
	display: flex;
	gap: .5rem;
	align-items: center;
	padding: 1rem;
}

.icon {
	font-size: 1.25rem;
}

.title {
	font-size: 16px;
	font-weight: 500;
}
</style>
