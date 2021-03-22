
def replace_quotes(string):
    """Заменяет кавычки в строке. ООО "Ромашка" заменит на ООО «Ромашка» """
    result = str(string)
    if result:
        total_quotes = result.count('"')
        while '"' in result:
            i = result.index('"')
            if result.count('"') <= total_quotes / 2:
                result = result[:i] + "»" + result[i + 1:]
            elif (len(result) > i + 1) and not (result[i + 1].isspace()):
                result = result[:i] + "«" + result[i + 1:]
            elif i > 0 and not result[i - 1].isspace():
                result = result[:i] + "»" + result[i + 1:]
            else:
                result = result[:i] + "»" + result[i + 1:]
    return result