from datetime import datetime


class RankingEngine:
    """Transparent 0-100 multi-criteria weighted scoring engine for BusBidder Spain."""

    PREFERRED_TIME_WINDOWS = {
        "morning": 9 * 60,     # 09:00
        "afternoon": 14 * 60,  # 14:00
        "evening": 19 * 60,    # 19:00
        "night": 22 * 60,      # 22:00
    }

    @staticmethod
    def normalize_lower_is_better(value: float, min_val: float, max_val: float) -> float:
        """Maps lower raw values closer to 100 and higher raw values closer to 0."""
        if max_val <= min_val:
            return 100.0
        score = 100.0 * (1.0 - (value - min_val) / (max_val - min_val))
        return max(0.0, min(100.0, score))

    @staticmethod
    def normalize_higher_is_better(value: float, min_val: float, max_val: float) -> float:
        """Maps higher raw values closer to 100 and lower raw values closer to 0."""
        if max_val <= min_val:
            return 100.0
        score = 100.0 * ((value - min_val) / (max_val - min_val))
        return max(0.0, min(100.0, score))

    @classmethod
    def _departure_to_minutes(cls, dep_time_str: str) -> int:
        try:
            parsed = datetime.strptime(str(dep_time_str).strip(), "%H:%M")
            return parsed.hour * 60 + parsed.minute
        except (ValueError, TypeError):
            return 9 * 60

    @classmethod
    def _preferred_target_minutes(cls, preferred_time: str) -> int:
        if not preferred_time:
            return 9 * 60
        key = str(preferred_time).strip().lower()
        if key in cls.PREFERRED_TIME_WINDOWS:
            return cls.PREFERRED_TIME_WINDOWS[key]
        try:
            parsed = datetime.strptime(key, "%H:%M")
            return parsed.hour * 60 + parsed.minute
        except ValueError:
            return 9 * 60

    @staticmethod
    def _flexibility_points(offer) -> float:
        """Converts ticket flexibility (changeable + refundable) to a 0-100 raw scale."""
        changeable = bool(getattr(offer, "changeable", False))
        refundable = bool(getattr(offer, "refundable", False))
        return (50.0 if changeable else 0.0) + (50.0 if refundable else 0.0)

    @classmethod
    def score_offers_detailed(cls, offers: list, profile) -> list[dict]:
        """
        Scores filtered offers on a 0-100 weighted sum model and returns results
        sorted by highest total_score with deterministic tie-breakers.
        """
        if not offers:
            return []

        prices = [float(getattr(o, "price", 0.0) or 0.0) for o in offers]
        durations = [float(getattr(o, "duration", 0) or 0) for o in offers]

        target_mins = cls._preferred_target_minutes(getattr(profile, "preferred_time", "Morning"))
        time_diffs = [
            float(abs(cls._departure_to_minutes(getattr(o, "departure_time", "09:00")) - target_mins))
            for o in offers
        ]
        flex_values = [cls._flexibility_points(o) for o in offers]

        min_p, max_p = min(prices), max(prices)
        min_d, max_d = min(durations), max(durations)
        min_t, max_t = min(time_diffs), max(time_diffs)
        min_f, max_f = min(flex_values), max(flex_values)

        weights = getattr(profile, "weights", {}) or {}
        w_price = float(weights.get("price", 0.0))
        w_dur = float(weights.get("duration", 0.0))
        w_time = float(weights.get("time", 0.0))
        w_flex = float(weights.get("flexibility", 0.0))

        detailed_results = []

        for offer, price, dur, t_diff, f_val in zip(offers, prices, durations, time_diffs, flex_values):
            p_score = cls.normalize_lower_is_better(price, min_p, max_p)
            d_score = cls.normalize_lower_is_better(dur, min_d, max_d)
            t_score = cls.normalize_lower_is_better(t_diff, min_t, max_t)
            f_score = cls.normalize_higher_is_better(f_val, min_f, max_f)

            total = (
                w_price * p_score
                + w_dur * d_score
                + w_time * t_score
                + w_flex * f_score
            )

            transfers = int(getattr(offer, "transfers", 0) or 0)
            changeable = bool(getattr(offer, "changeable", False))
            refundable = bool(getattr(offer, "refundable", False))
            rating = float(getattr(offer, "rating", 4.0) or 4.0)

            detailed_results.append({
                "offer": offer,
                "values": {
                    "price": price,
                    "duration": dur,
                    "departure_time": getattr(offer, "departure_time", "N/A"),
                    "time_diff_mins": int(t_diff),
                    "transfers": transfers,
                    "changeable": changeable,
                    "refundable": refundable,
                    "flex_points": f_val,
                    "rating": rating,
                },
                "scores": {
                    "price": round(p_score, 1),
                    "duration": round(d_score, 1),
                    "time": round(t_score, 1),
                    "flexibility": round(f_score, 1),
                },
                "total_score": round(total, 2),
            })

        # Primary sort by highest total score; deterministic tie-breakers by lower price,
        # shorter duration, and fewer transfers.
        detailed_results.sort(
            key=lambda item: (
                -item["total_score"],
                item["values"]["price"],
                item["values"]["duration"],
                item["values"]["transfers"],
            )
        )
        return detailed_results

    @classmethod
    def rank_offers(cls, offers: list, profile) -> list[tuple]:
        """Returns [(offer, total_score), ...] sorted from highest to lowest score."""
        detailed = cls.score_offers_detailed(offers, profile)
        return [(item["offer"], item["total_score"]) for item in detailed]

    @staticmethod
    def generate_top_explanation(
        top_item: dict,
        all_items: list[dict],
        profile,
        profile_label: str = "Selected Profile",
    ) -> str:
        """
        Generates a data-backed explanation for the #1 offer with strengths,
        trade-offs/disadvantages, and explicit framing under selected weights & assumptions.
        """
        offer = top_item["offer"]
        vals = top_item["values"]
        scores = top_item["scores"]
        total = top_item["total_score"]

        advantages = []
        disadvantages = []

        if vals["transfers"] == 0:
            advantages.append("a direct route (0 transfers)")
        else:
            disadvantages.append(f"{vals['transfers']} transfer(s)")

        avg_price = sum(x["values"]["price"] for x in all_items) / max(1, len(all_items))
        if scores["price"] >= 70.0 or vals["price"] <= avg_price:
            advantages.append(f"competitive price (€{vals['price']:.2f}, price score {scores['price']}/100)")
        else:
            disadvantages.append(
                f"higher price (€{vals['price']:.2f} vs. €{avg_price:.2f} average, price score {scores['price']}/100)"
            )

        if scores["duration"] >= 70.0:
            advantages.append(f"shorter trip duration ({vals['duration']/60:.1f}h, duration score {scores['duration']}/100)")
        elif scores["duration"] <= 40.0:
            disadvantages.append(f"longer trip duration ({vals['duration']/60:.1f}h, duration score {scores['duration']}/100)")

        pref_label = getattr(profile, "preferred_time", "Morning")
        if scores["time"] >= 70.0:
            advantages.append(f"convenient {vals['departure_time']} departure for {pref_label} preference (time score {scores['time']}/100)")
        elif scores["time"] <= 40.0:
            disadvantages.append(
                f"less convenient {vals['departure_time']} departure ({vals['time_diff_mins']} min from target, time score {scores['time']}/100)"
            )

        if vals["changeable"] and vals["refundable"]:
            advantages.append("full flexibility (changeable and refundable)")
        elif vals["changeable"]:
            advantages.append("changeable ticket option")
            disadvantages.append("non-refundable fare")
        elif vals["refundable"]:
            advantages.append("refundable ticket option")
            disadvantages.append("non-changeable fare")
        else:
            disadvantages.append("restricted fare (neither changeable nor refundable)")

        w = getattr(profile, "weights", {}) or {}
        dominant_criteria = [k for k, val in w.items() if float(val) >= 0.50]
        dominance_note = ""
        if dominant_criteria:
            dominance_note = (
                f" Note: High weight on {', '.join(dominant_criteria)} strongly shapes this outcome and can overshadow lower scores in other areas."
            )

        adv_text = ", ".join(advantages) if advantages else "balanced performance across criteria"
        dis_text = ", ".join(disadvantages) if disadvantages else "no major trade-offs against peers"

        weights_summary = (
            f"price {int(round(w.get('price', 0)*100))}%, "
            f"duration {int(round(w.get('duration', 0)*100))}%, "
            f"time {int(round(w.get('time', 0)*100))}%, "
            f"flexibility {int(round(w.get('flexibility', 0)*100))}%"
        )

        return (
            f"Why #{1} ({offer.company} at {vals['departure_time']} on {offer.date}) ranks first with {total:.2f}/100:\n"
            f"  • Advantages: Includes {adv_text}.\n"
            f"  • Disadvantages / Trade-offs: Includes {dis_text}.\n"
            f"  • Framing: Best only under your selected constraints, scoring assumptions, and [{profile_label}] "
            f"weights ({weights_summary}), not an objectively universal choice.{dominance_note}"
        )