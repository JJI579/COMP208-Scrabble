<script lang='ts' setup>

</script>


<template>
    <div class="content">
        CONTENT HERE
        should be variable with all details about the previous Game
    </div>
    <div class="actions">
        <RouterLink :to="{'name': 'create'}">
            <button>
                Create new Game
            </button>
        </RouterLink>
        <RouterLink :to="{'name': 'join'}">
            <button>
                Join a new Game
            </button>
        </RouterLink>

    </div>
</template>


<style lang='css' scoped>

</style>