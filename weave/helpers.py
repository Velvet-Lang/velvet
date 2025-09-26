def expand_macros(code: str, macros: Dict[str, str]) -> str:
    # Simple text-based expansion (replace macro calls with body)
    for name, body in macros.items():
        # Stub: Assume macro like inc(x) -> body with x replaced
        code = re.sub(rf'{name}\((.*?)\)', lambda m: body.replace('~x', m.group(1)), code)
    return code
