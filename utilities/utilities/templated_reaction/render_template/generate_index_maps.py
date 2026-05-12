def generate_index_maps(label_index_map: dict[int | str, int]) -> list[dict[int | str, int]]:
    label_index_map_list = list(label_index_map.items())
    all_combinations = []

    def recursive(current_combination: dict[str | int, int], index: int):
        # base case
        if index == len(label_index_map_list):
            if current_combination not in all_combinations:
                all_combinations.append(current_combination)
            return
        key, value = label_index_map_list[index]
        for i in range(value):
            new_combination = current_combination | {key: i}
            recursive(new_combination, index + 1)

    recursive({}, 0)
    return all_combinations
