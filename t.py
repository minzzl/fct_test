505 |         "any" => Some("Any"),
    |                  ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/unicode.rs:506:23
    |
506 |         "assigned" => Some("Assigned"),
    |                       ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/unicode.rs:507:20
    |
507 |         "ascii" => Some("ASCII"),
    |                    ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Ok` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/unicode.rs:519:5
    |
519 |     Ok(canonical_value(scripts, normalized_value))
    |     ^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Ok` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/unicode.rs:556:9
    |
556 |         Ok(PROPERTY_NAMES
    |         ^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Ok` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/unicode.rs:613:9
    |
613 |         Ok(PROPERTY_VALUES
    |         ^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Err` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/unicode.rs:685:21
    |
685 |             None => Err(Error::PropertyValueNotFound),
    |                     ^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Ok` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/unicode.rs:686:24
    |
686 |             Some(i) => Ok(AGES[..=i].iter().map(|&(_, classes)| classes)),
    |                        ^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Ok` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/unicode.rs:709:24
    |
709 |             "ASCII" => Ok(hir_class(&[('\0', '\x7F')])),
    |                        ^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Ok` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/unicode.rs:710:22
    |
710 |             "Any" => Ok(hir_class(&[('\0', '\u{10FFFF}')])),
    |                      ^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Ok` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/unicode.rs:714:17
    |
714 |                 Ok(cls)
    |                 ^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/utf8.rs:360:28
    |
360 |                     return Some(Utf8Sequence::One(ascii_range));
    |                            ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/utf8.rs:380:24
    |
380 |                 return Some(Utf8Sequence::from_encoded_range(
    |                        ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/utf8.rs:398:13
    |
398 |             Some((
    |             ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/utf8.rs:418:13
    |
418 |             Some(Utf8Range::new(start, end))
    |             ^^^^ not found in this scope

Some errors have detailed explanations: E0405, E0408, E0412, E0416, E0425, E0463, E0531.
error: could not compile `regex-syntax` (lib) due to 1315 previous errors
root@d599bb9f1a94:/home/root/app.energy# cargo clean
     Removed 192 files, 34.1MiB total
root@d599bb9f1a94:/home/root/app.energy# rustc --version
rustc 1.75.0 (82e1608df 2023-12-21)
