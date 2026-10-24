#[cfg(test)]
mod generated_rule_tests {
    use super::*;

    const NAMESPACE: &str = "codes.example";
    const FAMILY: &str = "synthetic-building-code";
    fn facts(width: i128) -> Vec<Fact<'static>> {
        vec![
            Fact { name: "occupancy", value: Value::Text("assembly") },
            Fact { name: "egress.clear_width", value: Value::Quantity { mantissa: width, scale: 0, unit: "[in_i]" } },
            Fact { name: "special_exception", value: Value::Bool(false) },
        ]
    }

    #[test]
    fn exact_edition_changes_result() {
        let f = facts(40);
        assert_eq!(evaluate(NAMESPACE, FAMILY, "2024", "", &f).unwrap()[0].decision, Decision::Satisfied);
        assert_eq!(evaluate(NAMESPACE, FAMILY, "2027", "", &f).unwrap()[0].decision, Decision::Violated);
        assert!(evaluate(NAMESPACE, FAMILY, "2025", "", &f).is_none());
        assert!(evaluate(NAMESPACE, FAMILY, "2024", "errata-1", &f).is_none());
        assert!(evaluate("other.example", FAMILY, "2024", "", &f).is_none());
    }

    #[test]
    fn unknown_is_never_equivalent_to_pass() {
        let empty: [Fact<'static>; 0] = [];
        assert_eq!(evaluate(NAMESPACE, FAMILY, "2024", "", &empty).unwrap()[0].decision, Decision::InsufficientFacts);
        let missing_width = [Fact { name: "occupancy", value: Value::Text("assembly") },
            Fact { name: "special_exception", value: Value::Bool(false) }];
        assert_eq!(evaluate(NAMESPACE, FAMILY, "2024", "", &missing_width).unwrap()[0].decision, Decision::InsufficientFacts);
        let mut dup = facts(40);
        dup.push(Fact { name: "egress.clear_width", value: Value::Quantity { mantissa: 100, scale: 0, unit: "[in_i]" } });
        assert_eq!(evaluate(NAMESPACE, FAMILY, "2024", "", &dup).unwrap()[0].decision, Decision::InsufficientFacts);
    }

    #[test]
    fn exemption_and_not_applicable_are_distinct() {
        let mut not_applicable = facts(12);
        not_applicable[0] = Fact { name: "occupancy", value: Value::Text("residential") };
        assert_eq!(evaluate(NAMESPACE, FAMILY, "2024", "", &not_applicable).unwrap()[0].decision, Decision::NotApplicable);
        let mut excepted = facts(12);
        excepted[2] = Fact { name: "special_exception", value: Value::Bool(true) };
        assert_eq!(evaluate(NAMESPACE, FAMILY, "2024", "", &excepted).unwrap()[0].decision, Decision::Excepted);
    }

    #[test]
    fn units_fixed_point_and_unsupported_are_explicit() {
        let wrong_units = [
            Fact { name: "occupancy", value: Value::Text("assembly") },
            Fact { name: "egress.clear_width", value: Value::Quantity { mantissa: 900, scale: 0, unit: "mm" } },
            Fact { name: "special_exception", value: Value::Bool(false) },
        ];
        // 900 mm is less than the 2024 illustrative threshold of 36 inches (914.4 mm).
        assert_eq!(evaluate(NAMESPACE, FAMILY, "2024", "", &wrong_units).unwrap()[0].decision, Decision::Violated);
        let exact_mm = [
            Fact { name: "occupancy", value: Value::Text("assembly") },
            Fact { name: "egress.clear_width", value: Value::Quantity { mantissa: 1016, scale: 0, unit: "mm" } },
            Fact { name: "special_exception", value: Value::Bool(false) },
        ];
        assert_eq!(evaluate(NAMESPACE, FAMILY, "2024", "", &exact_mm).unwrap()[0].decision, Decision::Satisfied);
        let incompatible = [
            Fact { name: "occupancy", value: Value::Text("assembly") },
            Fact { name: "egress.clear_width", value: Value::Quantity { mantissa: 40, scale: 0, unit: "A" } },
            Fact { name: "special_exception", value: Value::Bool(false) },
        ];
        assert_eq!(evaluate(NAMESPACE, FAMILY, "2024", "", &incompatible).unwrap()[0].decision, Decision::InsufficientFacts);
        assert_eq!(evaluate(NAMESPACE, FAMILY, "2024", "", &facts(40)).unwrap()[1].decision, Decision::Unsupported);
        assert_eq!(compare_fixed(3, 1, 30, 2), Some(Ordering::Equal));
        assert_eq!(compare_quantity(1016, 0, "mm", 40, 0, "[in_i]"), Some(Ordering::Equal));
        assert_eq!(compare_fixed(i128::MAX, 0, 1, 18), None);
    }

    #[test]
    fn multiple_code_families_are_isolated() {
        let ok = [Fact { name: "alarm.installed", value: Value::Bool(true) }];
        let results = evaluate(NAMESPACE, "synthetic-fire-code", "2026", "", &ok).unwrap();
        assert_eq!(results.len(), 1);
        assert_eq!(results[0].decision, Decision::Satisfied);
        assert_eq!(EDITIONS.len(), 3);
    }
}