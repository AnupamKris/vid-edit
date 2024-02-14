<template>
  <main>
    <div class="mainbar">
      <div class="sidebar">
        <input
          type="file"
          ref="inputRef"
          @change="handleFileChange"
          tabindex="-1"
          :disabled="videoSelected"
        />
        <button @click="openFile">Open</button>
        <div class="marker-times">
          <div
            @click.self="selectMarker(index)"
            class="mark"
            v-for="(marker, index) in markers"
            :class="{ selected: selectedMarker === index }"
          >
            <p>{{ index }}</p>
            <button @click="updateMarker(index, 0.01)">
              <ion-icon name="remove-circle-outline"></ion-icon>
            </button>
            <input type="text" v-model="markers[index]" />
            <button @click="updateMarker(index, 0.01)">
              <ion-icon name="add-circle-outline"></ion-icon>
            </button>
            <button @click="deleteMarker(index)" class="red">
              <ion-icon name="close-circle-outline"></ion-icon>
            </button>
          </div>
        </div>
        <button @click="clipVideo" :disabled="!videoSelected">Clip</button>
      </div>
      <div class="viddiv">
        <video
          @click="togglePause"
          src=""
          ref="video"
          @timeupdate="updateTime"
        ></video>
      </div>
    </div>
    <div class="controls" v-if="video">
      <div class="inactive" :class="{ cover: !videoSelected }"></div>
      <div class="wrapper">
        <div class="seek-slider">
          <input
            ref="sliderRef"
            :value="seek"
            @input="changeSeek"
            type="range"
            :min="0"
            :max="100"
            :step="0.01"
          />
        </div>
        <div
          class="markers-wrapper"
          @mousemove="dragMarker"
          @mouseup="draggingMarker = null"
        >
          <div
            class="marker"
            :style="{ left: (marker / video.duration) * 100 + '%' }"
            v-for="(marker, index) in markers"
            @click="selectMarker(index)"
            :class="{ selected: selectedMarker == index }"
            @mousedown="draggingMarker = index"
            @mouseup="draggingMarker = null"
          >
            <ion-icon name="pricetag" style="fill: white"></ion-icon>
          </div>
          <div
            class="section"
            :style="{
              left: (piece.start / video.duration) * 100 + '%',
              width: (piece.end / video.duration) * 100 + '%',
            }"
            v-for="piece in pieces"
          ></div>
        </div>
      </div>

      <div class="ctrls">
        <p>
          {{ padInt(video.currentTime / 60) }}:{{
            padInt(video.currentTime % 60)
          }}
          /
          {{ padInt(video.duration / 60) }}:{{ padInt(video.duration % 60) }}
        </p>

        <div class="buttons">
          <div class="ctl" @click="skipBack">
            <ion-icon name="play-skip-back-circle-outline"></ion-icon>
          </div>
          <div class="ctl" @click="playBackward">
            <ion-icon name="play-back-circle-outline"></ion-icon>
          </div>
          <div class="ctl" @click="togglePause">
            <ion-icon name="pause-circle-outline" v-if="!isPaused"></ion-icon>
            <ion-icon name="play-circle-outline" v-else></ion-icon>
          </div>
          <div class="ctl" @click="playForward">
            <ion-icon name="play-forward-circle-outline"></ion-icon>
          </div>
          <div class="ctl" @click="skipEnd">
            <ion-icon name="play-skip-forward-circle-outline"></ion-icon>
          </div>
        </div>

        <div class="buttons">
          <div class="ctl" @click="addMarker">
            <ion-icon name="crop-outline"></ion-icon>
          </div>
          <div class="slider-wrapper">
            <input v-model="volume" type="range" :min="0" :max="100" />
          </div>
        </div>
      </div>
    </div>
  </main>
  <div class="loadiv" v-if="loading">loading...</div>
</template>

<script setup>
import {
  readDir,
  removeFile,
  writeTextFile,
  BaseDirectory,
} from "@tauri-apps/api/fs";
import { Command } from "@tauri-apps/api/shell";
import { open, save } from "@tauri-apps/api/dialog";
import { convertFileSrc } from "@tauri-apps/api/tauri";

const sliderRef = ref(null);
const filepath = ref("");
const video = ref(null);
const seek = ref(0);
const volume = ref(50);
const videoSelected = ref(false);
const selectedMarker = ref(null);
const padInt = (num) => parseInt(num).toString().padStart(2, 0);
const inputRef = ref(null);
const markers = ref([]);
const loading = ref(false);
const isPaused = ref(false);
const draggingMarker = ref(null);
const pieces = computed(() => {
  let start = 0;
  let end = 0;
  let result = [];
  // sort markers in ascending order
  markers.value.sort((a, b) => a - b);

  console.log(markers.value);
  for (let i = 0; i < markers.value.length; i++) {
    if (i % 2 === 0) {
      start = markers.value[i];
      console.log(start);
    } else {
      end = markers.value[i] - start;
      result.push({ start, end });
      console.log(start);
    }
  }
  return result;
});

const updateTime = () => {
  seek.value = (video.value.currentTime / video.value.duration) * 100;
};

const addMarker = () => {
  markers.value.push(video.value.currentTime);
  markers.value.sort((a, b) => a - b);
};

const handleFileChange = (e) => {
  console.log(e.target.files[0]);
  const file = e.target.files[0];

  video.value.src = URL.createObjectURL(file);
  video.type = "video/mp4";
  video.value.play();
  video.value.volume = volume.value / 100;
  videoSelected.value = true;

  inputRef.value.value.focus();
};

const togglePause = () => {
  if (video.value.paused) {
    video.value.play();
    isPaused.value = false;
  } else {
    video.value.pause();
    isPaused.value = true;
  }
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

const skipBack = () => {
  video.value.currentTime = 0;
};
const skipEnd = () => {
  video.value.currentTime = video.value.duration;
};
const playForward = () => {
  video.value.currentTime += 1;
};
const playBackward = () => {
  video.value.currentTime -= 1;
};

const changeSeek = (e) => {
  if (typeof e === "number") {
    seek.value = e;
  } else {
    video.value.currentTime = (e.target.value / 100) * video.value.duration;
    console.log(e);
  }
};

const updateMarker = (index, val) => {
  markers.value[index] += val;
  video.value.currentTime = markers.value[index];
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

const selectMarker = (ind) => {
  if (selectedMarker.value === ind) {
    selectedMarker.value = null;
  } else {
    selectedMarker.value = ind;
  }
};

const openFile = async () => {
  const file = await open({ directory: false, multiple: false });
  console.log(file);
  if (file) {
    filepath.value = file;
    let fileSrc = convertFileSrc(file);
    video.value.src = fileSrc;
    video.value.type = "video/mp4";
    video.value.play();
    video.value.volume = volume.value / 100;
    videoSelected.value = true;
  }
};

const clipVideo = async () => {
  let piecess = pieces.value;
  let file = filepath.value;
  let outputPath = await save({
    filters: [
      {
        name: "Video",
        extensions: ["mp4"],
      },
    ],
  });
  if (!outputPath) {
    return;
  }
  console.log(pieces.value.length);
  let progress = 0;
  let total = pieces.value.length;
  for (let i = 0; i < pieces.value.length; i++) {
    let piece = pieces.value[i];
    let start = piece.start;
    let end = piece.end;
    let output = filepath.value.replace(".mp4", `_${i}.mp4`);
    let exec = false;
    console.log(output);
    // console.log("-i", filepath.value.replaceAll("\\", "/"), "-ss", start.toString(), "-t", end.toString(), "-c", "copy", output.replaceAll("\\", "/"));
    let command = Command.sidecar("trim", [
      filepath.value.replaceAll("\\", "/"),
      start.toString(),
      end.toString(),
      output.replaceAll("\\", "/"),
    ]);
    loading.value = true;
    command.on("error", (err) => {
      console.log("Error", err);
    });
    command.stdout.on("data", (data) => {
      console.log("Data", data);
    });
    command.on("close", (code) => {
      console.log("Closed", code, ++progress, total);
      // loading.value = false;
    });
    await command.execute();
  }
  let vidlist = pieces.value.map((piece, i) => {
    return (
      "file '" +
      filepath.value.replace(".mp4", `_${i}.mp4`).replaceAll("\\", "/") +
      "'"
    );
  });
  let txtLoc = filepath.value.replace(".mp4", "_list.txt");
  await writeTextFile(txtLoc, vidlist.join("\n"));

  console.log([outputPath, txtLoc]);

  let command = Command.sidecar("concat", [outputPath, txtLoc]);
  loading.value = true;
  command.on("error", (err) => {
    console.log("Error", err);
  });
  command.stdout.on("data", (data) => {
    console.log("Data", data);
  });
  command.on("close", (code) => {
    console.log("Closed", code);
  });
  await command.execute();
  let files = pieces.value.map((piece, i) => {
    return filepath.value.replace(".mp4", `_${i}.mp4`);
  });
  files.forEach(async (file) => {
    removeFile(file);
  });
  removeFile(txtLoc);
  loading.value = false;
  console.log("Clipped");

  // delete files
};

const dragMarker = (e) => {
  if (draggingMarker.value !== null) {
    console.log("dragging", e);
    let movement = e.movementX;
    markers.value[draggingMarker.value] +=
      (movement / 100) * video.value.duration;
  }
};

// move marker on arrow keys
const moveMarker = (e) => {
  if (selectedMarker.value !== null) {
    if (e.key === "ArrowRight") {
      markers.value[selectedMarker.value] += 0.1;
    } else if (e.key === "ArrowLeft") {
      markers.value[selectedMarker.value] -= 0.1;
    }
  }
};

const moveVideo = (e) => {
  console.log("moveVideo", e.key, video.value.currentTime);
  if (e.key === "ArrowRight") {
    video.value.currentTime += 3;
  } else if (e.key === "ArrowLeft") {
    video.value.currentTime -= 3;
  } else if (e.key === "ArrowUp") {
    video.value.currentTime += 1 / 60;
  } else if (e.key === "ArrowDown") {
    video.value.currentTime -= 1 / 60;
  }
};

const deleteMarker = (index) => {
  markers.value.splice(index, 1);
};

const handleMove = (e) => {
  console.log("hnadline", e.key);
  if (e.key === "M" || e.key === "m") {
    addMarker();
  } else if (e.key === " ") {
    togglePause();
  } else if (selectedMarker.value !== null) {
    if (e.key === "Delete") {
      markers.value.splice(selectedMarker.value, 1);
      selectedMarker.value = null;
      return;
    }
    moveMarker(e);
  } else {
    moveVideo(e);
  }
};

window.addEventListener("keydown", handleMove);

watch(volume, changeVolume);
watch(seek, changeSeek);
</script>

<style lang="scss" scoped>
.loadiv {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  width: 100%;
  position: absolute;
  top: 0;
  left: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 100;
  color: white;
  font-size: 2em;
}

main {
  padding: 10px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;

  height: 100vh;
  width: 100%;
  background: #141414;
  overflow: hidden;

  .mainbar {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: calc(100% - 100px);

    .sidebar {
      width: 300px;
      background: #292929;
      height: 100%;
      border-radius: 10px;

      display: flex;
      // justify-content: center;
      align-items: center;
      flex-direction: column;

      .marker-times {
        width: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;

        .mark {
          width: 80%;
          display: flex;
          justify-content: space-between;
          align-items: center;

          border-radius: 10px;
          padding: 2px 5px;

          margin-top: 5px;

          color: #ffffff;

          transition: 0.3s;

          p {
            width: 20px;
            text-align: center;

            display: flex;
            justify-content: center;
            align-items: center;
            margin-right: auto;
          }

          input {
            width: 100px;
            height: 30px;
            border-radius: 5px;
            border: none;
            outline: none;
            margin: 0 10px;

            background: #141414;
            color: #ffffff;
            text-align: center;
          }

          button {
            background: #141414;
            width: 20px;
            height: 20px;
            border-radius: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 0;
          }

          .red {
            color: #ffffff;
            background: #ff5b5b;
            margin-left: 10px;
          }
        }

        .selected {
          background: #0088ff;
        }
      }

      button {
        width: 80%;
        border: none;
        outline: none;

        background: #0088ff;
        height: 40px;
        border-radius: 5px;
        color: white;
        margin-top: 10px;
      }

      input[type="file"] {
        display: none;
      }
    }

    .viddiv {
      width: calc(100% - 300px);
      min-width: calc(100% - 300px);
      height: 100%;
      border-radius: 10px;
      margin-left: 10px;
      overflow: hidden;
      background: #292929;

      video {
        width: 100%;
        max-height: 100%;
      }

      // max-width: 500px;
    }
  }

  .controls {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    height: 100px;
    flex-direction: column;
    position: relative;

    .inactive {
      display: none;
    }

    .cover {
      display: flex;
      height: calc(100% + 20px);
      width: calc(100% + 20px);
      position: absolute;
      background: #14141455;
      backdrop-filter: blur(5px);
      z-index: 10;

      top: calc(50% + 20px);
      left: 50%;

      transform: translate(-50%, -50%);
    }

    .ctrls {
      display: flex;
      justify-content: space-between;
      align-items: center;
      width: 100%;
      color: #bebebe;

      p {
        font-family: "Roboto Mono";
      }

      .buttons {
        display: flex;
        justify-content: center;
        align-items: center;

        .ctl {
          display: flex;
          justify-content: center;
          align-items: center;

          font-size: 24px;
        }

        .slider-wrapper {
          height: 18px;
          overflow: hidden;
          border-radius: 10px;
          margin: 0 10px;
        }

        input[type="range"] {
          -webkit-appearance: none;
          width: 100%;
          background: #292929;
          border-radius: 5px;
          outline: none;
        }

        input[type="range"]::-webkit-slider-thumb {
          -webkit-appearance: none;
          height: 18px;
          width: 18px;
          border-radius: 10px;
          background: #ffffff;
          cursor: ew-resize;
          box-shadow: 0 0 2px 0 #555;
          transition: background 0.3s ease-in-out;
          z-index: 2;
          border: 2px solid #0088ff;
          box-shadow: -15010px 0 0 15000px #0088ff;
        }

        input[type="range"]::-webkit-slider-runnable-track {
          -webkit-appearance: none;
          box-shadow: none;
          border: none;
        }
      }
    }
  }
}

.wrapper {
  margin-top: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  position: relative;

  .markers-wrapper {
    width: calc(100% - 8px);
    height: 20px;
    top: -20px;
    position: absolute;
    z-index: 0;
  }

  .marker {
    position: absolute;
    // top: -10px;
    // left: 50%;

    top: 7px;
    width: 5px;
    height: 20px;
    transform: translate(-50%, -50%);
    // background-color: #a4a4a4;
    z-index: 1;

    pointer-events: all;

    display: flex;
    justify-content: center;
    align-items: center;

    ion-icon {
      min-width: 20px;
      height: 20px;
      pointer-events: none;

      transform: rotateZ(135deg);
    }

    &.selected {
      ion-icon {
        border: 2px solid #0088ff;
      }
    }
  }

  .section {
    height: 10px;
    top: 2px;
    background: #bebebe;
    position: absolute;
  }
}

.seek-slider {
  width: 100%;
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
    background: #292929;
    border-radius: 5px;
    outline: none;
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
    box-shadow: -15002px 0 0 15000px #0088ff;
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
