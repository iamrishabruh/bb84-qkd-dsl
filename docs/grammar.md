# BB84 DSL grammar (EBNF)

Lexical rules are defined first; the parser consumes the token stream produced by the lexer.

## Lexical structure

```ebnf
(* Whitespace: space, tab, carriage return, newline *)
WS            ::= { " " | "\t" | "\r" | "\n" } ;

(* Line comments run from # to end of line *)
COMMENT       ::= "#" { any character except newline } ;

IDENT         ::= ( letter | "_" ) { letter | digit | "_" } ;
letter        ::= "a"…"z" | "A"…"Z" ;
digit         ::= "0"…"9" ;

INT           ::= digit { digit } ;
FLOAT         ::= digit { digit } "." digit { digit } ;

keyword       ::= "seed" | "noise" | "error_threshold" | "eavesdrop" | "on" | "off"
                | "qubit" | "alice_send" | "bob_measure" | "rect" | "diag"
                | "sift_keys" | "check_eavesdropping" | "generate_key" | "print" ;
```

An `IDENT` that matches a keyword is tokenized as that keyword, not as an identifier.

## Syntax

```ebnf
program       ::= { statement } EOF ;

statement     ::= seed_stmt
                | noise_stmt
                | error_threshold_stmt
                | eavesdrop_stmt
                | qubit_decl
                | alice_send_stmt
                | bob_measure_stmt
                | sift_keys_stmt
                | check_eavesdropping_stmt
                | generate_key_stmt
                | print_stmt ;

seed_stmt              ::= "seed" INT ;
noise_stmt             ::= "noise" ( FLOAT | INT ) ;
error_threshold_stmt   ::= "error_threshold" ( FLOAT | INT ) ;
eavesdrop_stmt         ::= "eavesdrop" ( "on" | "off" ) ;

qubit_decl             ::= "qubit" IDENT ;
alice_send_stmt        ::= "alice_send" IDENT ;
bob_measure_stmt       ::= "bob_measure" IDENT ( "rect" | "diag" ) ;

sift_keys_stmt         ::= "sift_keys" ;
check_eavesdropping_stmt ::= "check_eavesdropping" ;
generate_key_stmt      ::= "generate_key" IDENT ;
print_stmt             ::= "print" IDENT ;
```

## Static constraints (checked by the interpreter)

- `bob_measure` rounds must appear in the same order as `alice_send`, and each pair must refer to the same qubit name.
- `sift_keys` requires exactly one `bob_measure` for every `alice_send`.
- `check_eavesdropping` must follow `sift_keys`.
- `generate_key` requires at least one sifted bit (a matching Alice/Bob basis pair).
- `noise`, `error_threshold`, and probabilities must lie in `[0, 1]`.

These constraints are not encoded in the context-free grammar above; they are runtime errors with source-aware reporting where available.
