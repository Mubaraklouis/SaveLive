const express = require("express");
const router = express.Router();
const { query } = require("../config/db");
const seedEvents = require("../data/seedEvents");

// POST /api/seed — Seed the database with fallback ACLED conflict events
router.post("/", async (req, res) => {
  try {
    let inserted = 0;
    let skipped = 0;
    const errors = [];

    for (const event of seedEvents) {
      try {
        await query(
          `INSERT INTO events (
            event_id_cnty, event_date, year, time_precision, disorder_type,
            event_type, sub_event_type, actor1, assoc_actor_1, inter1,
            actor2, assoc_actor_2, inter2, interaction, civilian_targeting,
            iso, region, country, admin1, admin2, admin3, location,
            latitude, longitude, geo_precision, source, source_scale,
            notes, fatalities, tags, timestamp
          ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
            $11, $12, $13, $14, $15, $16, $17, $18, $19, $20,
            $21, $22, $23, $24, $25, $26, $27, $28, $29, $30, $31
          )
          ON CONFLICT (event_id_cnty) DO NOTHING`,
          [
            event.event_id_cnty, event.event_date, event.year,
            event.time_precision, event.disorder_type, event.event_type,
            event.sub_event_type, event.actor1, event.assoc_actor_1,
            event.inter1, event.actor2, event.assoc_actor_2,
            event.inter2, event.interaction, event.civilian_targeting,
            event.iso, event.region, event.country, event.admin1,
            event.admin2, event.admin3, event.location, event.latitude,
            event.longitude, event.geo_precision, event.source,
            event.source_scale, event.notes, event.fatalities,
            event.tags, event.timestamp,
          ]
        );
        inserted++;
      } catch (err) {
        skipped++;
        errors.push({
          event_id_cnty: event.event_id_cnty,
          error: err.message,
        });
      }
    }

    res.status(201).json({
      message: "Database seeded with conflict events",
      total: seedEvents.length,
      inserted,
      skipped,
      errors: errors.length > 0 ? errors : undefined,
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// DELETE /api/seed — Clear all seeded events
router.delete("/", async (req, res) => {
  try {
    const result = await query("DELETE FROM events");
    res.json({
      message: "All events cleared",
      deleted: result.rowCount,
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET /api/seed/status — Check if seed data exists
router.get("/status", async (req, res) => {
  try {
    const result = await query("SELECT COUNT(*) FROM events");
    const count = parseInt(result.rows[0].count, 10);
    res.json({
      seeded: count > 0,
      event_count: count,
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
