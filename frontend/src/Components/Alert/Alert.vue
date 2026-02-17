<script lang='ts' setup>
import useAlertStore from '../Stores/alert';

const alertStore = useAlertStore();

</script>


<template>
    <div class="alert" :class="{'alert--active': alertStore.isActive}">
        {{ alertStore.currentAlert?.text }}
    </div>
</template>


<style lang='css' scoped>
    .alert {
        position: fixed;
        right: -35%;
        top: 5%;
        z-index: 100000000;
        height: 3.5rem;
        min-width: 30%;
        line-height: 1.5em;
        background-color: blue;
        transition: 0.2s ease-in all;
        display: flex;
        align-items: center;
        padding-left: 1rem;
        border-radius: 10px;
    }

    .alert--active {
        right: 10%;
    }
</style>