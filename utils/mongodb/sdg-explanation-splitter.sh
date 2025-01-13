#!/bin/env bash
awk '{
  if (NR % 10000 == 1) {
    file = sprintf("split_part_%03d.json", int(NR/10000))
  }
  print $0 >> file
}' sdg_explanations.json
