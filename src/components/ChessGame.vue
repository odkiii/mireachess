<script setup>
import { TheChessboard } from "vue3-chessboard";
import "vue3-chessboard/style.css";
</script>

<template title>
  <div>
    <h1>MireaChess</h1>
    <div id="board">
      <TheChessboard/>
    </div>
    <div id="status">ходят белые</div>
    <div id="moves">e1m1</div>
    <div className="menu">
      <button>Ход назад</button>
      <button>Ход вперед</button>
      <button>Игра заново</button>
      <select>
        <option value="1">Слабый бот</option>
        <option value="2">Средний бот</option>
        <option value="3">Сильный бот</option>
      </select>
    </div>
  </div>
</template>

<style>
#board {
  margin: 20px ;
  border: 2px solid black;
  width: auto;
  height: auto;
}

.menu {
  display: grid;
  grid-template-columns: 20% 20% 20% 40%;
  margin: auto;
  width: 400px;
  height: auto;
  border: 2px solid black;
}

.menu button {
  margin: 10px;
}

.menu select {
  margin: 10px;
}
</style>
