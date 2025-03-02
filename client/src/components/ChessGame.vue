<script setup>
import { ref, onMounted } from "vue";
import { TheChessboard } from "vue3-chessboard";
import "vue3-chessboard/style.css";
import axios from "axios";

const isGameStarted = ref(false); // Переменная для отслеживания состояния игры
const selectedDifficulty = ref("1"); // Переменная для хранения выбранного уровня сложности
const selectedColor = ref("w");
const moveHistory = [];
let boardAPI;
const boardConfigForWhite = {
  coordinates: true,
  orientation: "white",
};

async function startGame() {
  let diff = 1;
  if (selectedDifficulty.value === "2") {
    diff = 10;
  } else if (selectedDifficulty.value === "3") {
    diff = 20;
  }
  console.log(diff);
  try {
    const response = await axios.post("http://localhost:8000/api/start", {
      diff: diff,
    });
    console.log(response.data);
  } catch (error) {
    console.error("Ошибка при отправке запроса: ", error);
  }
  isGameStarted.value = true;

  if (selectedColor.value === "b") {
    boardAPI?.toggleOrientation();
    sendMove(boardAPI?.getFen());
  }
}

function recordMove() {
  const lastMove = boardAPI?.getLastMove();
  moveHistory.push(lastMove.lan);
  console.log(moveHistory);
  if (lastMove.color === selectedColor.value) {
    sendMove(lastMove.after);
  }
}

function resetGame() {
  boardAPI?.resetBoard();
  moveHistory.value = [];
}

onMounted(() => {
  const script = document.createElement("script");
  script.src = "https://telegram.org/js/telegram-web-app.js";
  script.async = true;
  document.body.appendChild(script);
});

async function sendMove(fen) {
  console.log(boardAPI?.getLastMove());

  const prompt = { fen: fen };
  try {
    const response = await axios.post("http://localhost:8000/api/move", prompt);

    boardAPI?.move(response.data.best_move);
  } catch (error) {
    console.error("Ошибка при отправке запроса: ", error);
  }
}

// let tg = window.Telegram.WebApp;
// let game = document.getElementById("game");

// game.addEventListener("click", () => {
//   document.getElementById("main").style.display == "none";
//   document.getElementById("menu").style.display == "block";
// });
</script>
<!-- // name: 'MyComponent',
  // mounted() {
  //   const script = document.createElement('script');
  //   script.src = "https://telegram.org/js/telegram-web-app.js";
  //   script.async = true;
  //   document.body.appendChild(script);
  // },
   -->

<template title>
  <div id="main" v-show="isGameStarted">
    <h1>MireaChess</h1>
    <div id="move-history">
      <div id="selectedOptions">
        <p>Выбранный цвет: {{ selectedColor === "w" ? "белые" : "чёрные" }}</p>
        <p>Уровень сложности: {{ selectedDifficulty }}</p>
      </div>
      <span v-if="moveHistory.length === 0">Сделайте первый ход!</span>
      <span v-else>
        <span v-for="(move, index) in moveHistory" :key="index"
          >{{ index + 1 }}. {{ move
          }}<span v-if="index < moveHistory.length - 1">, </span></span
        >
      </span>
    </div>
    <div id="board">
      <TheChessboard
        @move="recordMove"
        :board-config="boardConfigForWhite"
        @board-created="(api) => (boardAPI = api)"
      />
      <!-- Слушаем событие хода -->
    </div>
    <div id="status">
      <div v-if="moveHistory === 0">Ходят белые</div>
      <div v-else>Ходят {{ currentColor === "w" ? "чёрные" : "белые" }}</div>
    </div>
    <div className="menu">
      <button @click="boardAPI?.toggleOrientation()">Повернуть доску</button>
      <button @click="resetGame()">Начать сначала</button>
      <button @click="boardAPI?.undoLastMove()">Ход назад</button>
    </div>
  </div>

  <!-- ТУТ БУДЕТ МЕНЮ ВЫБОРА СЛОЖНОСТИ БОТА И ВСЯКИЕ НАСТРОЙКИ -->
  <div id="start" v-show="!isGameStarted">
    <h2>Добро пожаловать!</h2>
    <h4>
      За кого играете:
      <select v-model="selectedColor">
        <option value="w">белые</option>
        <option value="b">чёрные</option>
      </select>
    </h4>
    <h4>
      Сложность бота:
      <select v-model="selectedDifficulty">
        <option value="1">Слабый</option>
        <option value="2">Средний</option>
        <option value="3">Сильный</option>
      </select>
    </h4>

    <button @click="startGame" id="game">Играть</button>
  </div>
</template>

<style>
#main {
  border: 2px solid red;
}

#start {
  border: 2px solid red;
  padding: 10px;
  margin: 10px;
}

#start select {
  width: 80px;
  height: 50px;
}

#board {
  margin: auto;
  border: 2px solid black;
  width: 700px;
  height: 700px;
}

.menu {
  display: grid;
  grid-template-columns: 33% 33% 33%;
  margin: auto;
  width: 400px;
  height: auto;
  border: 2px solid black;
  font-size: 12px;
}

.menu button {
  margin: 10px;
  padding: 5px;
}

.menu select {
  margin: 10px;
  padding: 5px;
}

#move-history {
  background-color: rgb(83, 83, 83);
  width: 704px;
  margin: 20px;
  margin-bottom: 0;
}

#game {
  border: 0;
  border-radius: 5px;
  width: 100px;
  height: 50px;
  text-align: center;
}
</style>
