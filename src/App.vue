<template>
  <input type="file" @change="handleFileChange" />
  <video src="" ref="video" @timeupdate="updateTime"></video>
  <div class="controls" v-if="video">
    <input v-model="volume" type="range" :min="0" :max="100" />
    <div class="ctl" @click="pauseVideo">
      <ion-icon name="pause-circle-outline"></ion-icon>
    </div>
    <div class="ctl" @click="playVideo">
      <ion-icon name="play-circle-outline"></ion-icon>
    </div>
    <div class="seek-slider">
      <input
        :value="seek"
        @input="changeSeek"
        type="range"
        :min="0"
        :max="100"
        :step="0.01"
      />
    </div>
    {{ parseInt(video.currentTime / 60) }}:{{
      parseInt(video.currentTime % 60)
    }}
    /
    {{ padInt(video.duration / 60) }}:{{ parseInt(video.duration % 60) }}
  </div>
</template>

<script setup>
import { computed, watch } from "vue";

const video = ref(null);
const seek = ref(0);
const volume = ref(1);
const videoControls = ref({});
const padInt = (num) => num.toString().padStart(2, 0);

const updateTime = () => {
  seek.value = (video.value.currentTime / video.value.duration) * 100;
};

let formattedTime;

const handleFileChange = (e) => {
  console.log(e.target.files[0]);
  const file = e.target.files[0];

  video.value.src = URL.createObjectURL(file);
  video.type = "video/mp4";
  video.value.play();
};

const pauseVideo = () => {
  video.value.pause();
};

const playVideo = () => {
  video.value.play();
};

const changeVolume = () => {
  video.value.volume = volume.value / 100;
};

const changeSeek = (e) => {
  if (typeof e === "number") {
    seek.value = e;
  } else {
    video.value.currentTime = (e.target.value / 100) * video.value.duration;
    console.log(e);
  }
};

const seekToPosition = (e) => {
  console.log(e);
  const bar = e.target;
  const x = e.clientX - bar.offsetLeft;
  const width = bar.offsetWidth;
  const percentage = (x / width) * 100;
  seek.value = percentage;
  video.value.currentTime = (percentage / 100) * video.value.duration;
};

watch(volume, changeVolume);
watch(seek, changeSeek);
</script>

<style lang="scss" scoped>
video {
  width: 350px;
}

.seek-slider {
  width: 80%;
  height: 20px;
  border-radius: 5px;
  overflow: hidden;

  position: relative;
  // .seek {
  //   position: absolute;
  //   top: 0;
  //   left: 0;
  //   height: 100%;
  //   z-index: 1;
  // }

  input[type="range"] {
    -webkit-appearance: none;
    width: 100%;
    background: #d3d3d3;
    border-radius: 5px;
  }

  input[type="range"]::-webkit-slider-thumb {
    -webkit-appearance: none;
    height: 20px;
    width: 7px;
    border-radius: 3px;
    background: #ffffff;
    cursor: ew-resize;
    box-shadow: 0 0 2px 0 #555;
    transition: background 0.3s ease-in-out;
    z-index: 2;
    border: 2px solid #0088ff;
    box-shadow: -407px 0 0 405px #0088ff;
  }

  input[type="range"]::-webkit-slider-runnable-track {
    -webkit-appearance: none;
    box-shadow: none;
    border: none;
  }
}

.time {
  width: 80%;
  height: 50px;

  .bar {
    width: 100%;
    height: 15px;
    background-color: #d3d3d3;
    border-radius: 10px;
    position: relative;
    .seek {
      width: 20px;
      height: 15px;
      background-color: #ff0000;
      border-radius: 10px;
    }
  }
}
</style>
