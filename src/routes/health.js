const express = require("express");
const router = express.Router();
const { query } = require("../config/db");

// Health check endpoint
router.get("/", async (req, res) => {
  try {
    const result = await query("SELECT NOW()");
    res.json({
      status: "ok",
      timestamp: result.rows[0].now,
      database: "connected",
    });
  } catch (err) {
    res.status(500).json({
      status: "error",
      database: "disconnected",
      error: err.message,
    });
  }
});

module.exports = router;
