# ScoutLens Model Validation

## Purpose

The position-aware similarity model was manually evaluated for face validity: whether its recommendations represent reasonably comparable positional and stylistic profiles.

## Method

Ten recognizable Premier League players were selected across forwards, midfielders, centre-backs, and fullbacks. Each player’s five closest recommendations was reviewed for positional and stylistic plausibility.

## Results

| Selected Player | Profile Tested | Assessment |
|---|---|---|
| Bukayo Saka | Winger / attacking midfielder | Pass |
| Erling Haaland | Central striker | Pass |
| Virgil van Dijk | Centre-back | Pass |
| Adrien Truffert | Fullback | Pass |
| Declan Rice | Central midfielder | Pass |
| Mohamed Salah | Wide attacker | Pass |
| Ollie Watkins | Central striker | Pass |
| Ibrahima Konaté | Centre-back | Pass |
| Dominik Szoboszlai | Central / attacking midfielder | Pass |
| Ola Aina | Fullback / wingback | Pass |

All ten players received positionally and stylistically plausible recommendations.

## Interpretation

The tests indicate that position-specific metrics and within-position standardization produce more credible recommendations than the original universal feature model. Reciprocal results such as Rice–Szoboszlai and Truffert–Aina also confirmed consistent distance calculations.

## Limitations

- Validation is manual and partly subjective.
- Similarity does not measure overall player quality.
- Results describe one season and do not predict future performance or transfer success.
- Broad position categories still combine distinct subroles.
- Future versions could introduce role clustering and out-of-sample validation.