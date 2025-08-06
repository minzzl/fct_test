    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/translate.rs:1250:40
     |
1250 |                     flags.multi_line = Some(enable);
     |                                        ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/translate.rs:1253:50
     |
1253 |                     flags.dot_matches_new_line = Some(enable);
     |                                                  ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/translate.rs:1256:40
     |
1256 |                     flags.swap_greed = Some(enable);
     |                                        ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/translate.rs:1259:37
     |
1259 |                     flags.unicode = Some(enable);
     |                                     ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/translate.rs:1262:34
     |
1262 |                     flags.crlf = Some(enable);
     |                                  ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Ok` in this scope
  --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/visitor.rs:31:9
   |
31 |         Ok(())
   |         ^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Ok` in this scope
  --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/visitor.rs:37:9
   |
37 |         Ok(())
   |         ^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Ok` in this scope
  --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/visitor.rs:42:9
   |
42 |         Ok(())
   |         ^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Ok` in this scope
  --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/visitor.rs:47:9
   |
47 |         Ok(())
   |         ^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/visitor.rs:163:43
    |
163 |             HirKind::Repetition(ref x) => Some(Frame::Repetition(x)),
    |                                           ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/visitor.rs:164:40
    |
164 |             HirKind::Capture(ref x) => Some(Frame::Capture(x)),
    |                                        ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/visitor.rs:167:17
    |
167 |                 Some(Frame::Concat { head: &x[0], tail: &x[1..] })
    |                 ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/visitor.rs:171:17
    |
171 |                 Some(Frame::Alternation { head: &x[0], tail: &x[1..] })
    |                 ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/visitor.rs:187:21
    |
187 |                     Some(Frame::Concat { head: &tail[0], tail: &tail[1..] })
    |                     ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/visitor.rs:194:21
    |
194 |                     Some(Frame::Alternation {
    |                     ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:381:50
    |
381 |         if rep.sub.properties().maximum_len() == Some(0) {
    |                                                  ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:383:58
    |
383 |             rep.max = rep.max.map(|n| cmp::min(n, 1)).or(Some(1));
    |                                                          ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:390:39
    |
390 |         if rep.min == 0 && rep.max == Some(0) {
    |                                       ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:392:46
    |
392 |         } else if rep.min == 1 && rep.max == Some(1) {
    |                                              ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:455:37
    |
455 |                         prior_lit = Some(bytes.to_vec());
    |                                     ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:470:49
    |
470 | ...                   prior_lit = Some(bytes.to_vec());
    |                                   ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Ok` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:881:9
    |
881 |         Ok(())
    |         ^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:1178:9
     |
1178 |         Some(first.start.len_utf8())
     |         ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:1188:9
     |
1188 |         Some(last.end.len_utf8())
     |         ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:1199:13
     |
1199 |             Some(rs[0].start.encode_utf8(&mut [0; 4]).to_string().into_bytes())
     |             ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:1211:9
     |
1211 |         Some(ClassBytes::new(self.ranges().iter().map(|r| {
     |         ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Ok` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:1296:20
     |
1296 |             return Ok(());
     |                    ^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Ok` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:1304:9
     |
1304 |         Ok(())
     |         ^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:1452:13
     |
1452 |             Some(1)
     |             ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:1464:13
     |
1464 |             Some(1)
     |             ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:1476:13
     |
1476 |             Some(vec![rs[0].start])
     |             ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:1488:9
     |
1488 |         Some(ClassUnicode::new(self.ranges().iter().map(|r| {
     |         ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Ok` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:1563:9
     |
1563 |         Ok(())
     |         ^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:1735:41
     |
1735 |             0b00_0000_0000_0000_0001 => Some(Look::Start),
     |                                         ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:1736:41
     |
1736 |             0b00_0000_0000_0000_0010 => Some(Look::End),
     |                                         ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:1737:41
     |
1737 |             0b00_0000_0000_0000_0100 => Some(Look::StartLF),
     |                                         ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:1738:41
     |
1738 |             0b00_0000_0000_0000_1000 => Some(Look::EndLF),
     |                                         ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:1739:41
     |
1739 |             0b00_0000_0000_0001_0000 => Some(Look::StartCRLF),
     |                                         ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:1740:41
     |
1740 |             0b00_0000_0000_0010_0000 => Some(Look::EndCRLF),
     |                                         ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:1741:41
     |
1741 |             0b00_0000_0000_0100_0000 => Some(Look::WordAscii),
     |                                         ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:1742:41
     |
1742 |             0b00_0000_0000_1000_0000 => Some(Look::WordAsciiNegate),
     |                                         ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:1743:41
     |
1743 |             0b00_0000_0001_0000_0000 => Some(Look::WordUnicode),
     |                                         ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:1744:41
     |
1744 |             0b00_0000_0010_0000_0000 => Some(Look::WordUnicodeNegate),
     |                                         ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:1745:41
     |
1745 |             0b00_0000_0100_0000_0000 => Some(Look::WordStartAscii),
     |                                         ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:1746:41
     |
1746 |             0b00_0000_1000_0000_0000 => Some(Look::WordEndAscii),
     |                                         ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:1747:41
     |
1747 |             0b00_0001_0000_0000_0000 => Some(Look::WordStartUnicode),
     |                                         ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:1748:41
     |
1748 |             0b00_0010_0000_0000_0000 => Some(Look::WordEndUnicode),
     |                                         ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:1749:41
     |
1749 |             0b00_0100_0000_0000_0000 => Some(Look::WordStartHalfAscii),
     |                                         ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:1750:41
     |
1750 |             0b00_1000_0000_0000_0000 => Some(Look::WordEndHalfAscii),
     |                                         ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:1751:41
     |
1751 |             0b01_0000_0000_0000_0000 => Some(Look::WordStartHalfUnicode),
     |                                         ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:1752:41
     |
1752 |             0b10_0000_0000_0000_0000 => Some(Look::WordEndHalfUnicode),
     |                                         ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:2373:45
     |
2373 |                         props.minimum_len = Some(xmin);
     |                                             ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:2383:45
     |
2383 |                         props.maximum_len = Some(xmax);
     |                                             ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:2399:26
     |
2399 |             minimum_len: Some(0),
     |                          ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:2400:26
     |
2400 |             maximum_len: Some(0),
     |                          ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:2425:43
     |
2425 |             static_explicit_captures_len: Some(0),
     |                                           ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:2435:26
     |
2435 |             minimum_len: Some(lit.0.len()),
     |                          ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:2436:26
     |
2436 |             maximum_len: Some(lit.0.len()),
     |                          ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:2444:43
     |
2444 |             static_explicit_captures_len: Some(0),
     |                                           ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:2463:43
     |
2463 |             static_explicit_captures_len: Some(0),
     |                                           ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:2473:26
     |
2473 |             minimum_len: Some(0),
     |                          ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:2474:26
     |
2474 |             maximum_len: Some(0),
     |                          ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:2495:43
     |
2495 |             static_explicit_captures_len: Some(0),
     |                                           ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:2547:27
     |
2547 |             if rep.max == Some(0) {
     |                           ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:2548:54
     |
2548 |                 inner.static_explicit_captures_len = Some(0);
     |                                                      ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:2577:26
     |
2577 |             minimum_len: Some(0),
     |                          ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:2578:26
     |
2578 |             maximum_len: Some(0),
     |                          ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:2586:43
     |
2586 |             static_explicit_captures_len: Some(0),
     |                                           ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:2601:21
     |
2601 |                     Some((len1, props.static_explicit_captures_len?))
     |                     ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:2603:42
     |
2603 |                 .and_then(|(len1, len2)| Some(len1.saturating_add(len2)));
     |                                          ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:2615:29
     |
2615 | ...                   Some(minimum_len.saturating_add(len));
     |                       ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Ok` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:2908:9
     |
2908 |         Ok(())
     |         ^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:2933:9
     |
2933 |         Some(look)
     |         ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:2953:5
     |
2953 |     Some(Class::Unicode(cls))
     |     ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:2972:5
     |
2972 |     Some(Class::Bytes(cls))
     |     ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:2995:5
     |
2995 |     Some(singletons)
     |     ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:3013:5
     |
3013 |     Some(singletons)
     |     ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Err` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:3029:16
     |
3029 |         return Err(hirs);
     |                ^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Err` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:3033:21
     |
3033 |         _ => return Err(hirs),
     |                     ^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Err` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:3036:16
     |
3036 |         return Err(hirs);
     |                ^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Err` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:3041:25
     |
3041 |             _ => return Err(hirs),
     |                         ^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Err` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:3050:20
     |
3050 |             return Err(hirs);
     |                    ^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Ok` in this scope
    --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/hir/mod.rs:3072:5
     |
3072 |     Ok(Hir::concat(concat))
     |     ^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Ok` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/parser.rs:252:9
    |
252 |         Ok(hir)
    |         ^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Ok` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/unicode.rs:105:13
    |
105 |             Ok(SimpleCaseFolder {
    |             ^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/unicode.rs:134:21
    |
134 |         self.last = Some(c);
    |                     ^^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Err` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/unicode.rs:247:36
    |
247 |                     None => return Err(Error::PropertyNotFound),
    |                                    ^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Ok` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/unicode.rs:250:17
    |
250 |                 Ok(match canon_name {
    |                 ^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Err` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/unicode.rs:253:44
    |
253 | ...                   None => return Err(Error::PropertyValueNotFound),
    |                                      ^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Err` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/unicode.rs:260:44
    |
260 | ...                   None => return Err(Error::PropertyValueNotFound),
    |                                      ^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Err` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/unicode.rs:267:44
    |
267 | ...                   None => return Err(Error::PropertyValueNotFound),
    |                                      ^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Err` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/unicode.rs:273:44
    |
273 | ...                   return Err(Error::PropertyValueNotFound)
    |                              ^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Ok` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/unicode.rs:311:24
    |
311 |                 return Ok(CanonicalClassQuery::Binary(canon));
    |                        ^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Ok` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/unicode.rs:315:20
    |
315 |             return Ok(CanonicalClassQuery::GeneralCategory(canon));
    |                    ^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Ok` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/unicode.rs:318:20
    |
318 |             return Ok(CanonicalClassQuery::Script(canon));
    |                    ^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Err` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/unicode.rs:320:9
    |
320 |         Err(Error::PropertyNotFound)
    |         ^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Ok` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/unicode.rs:363:13
    |
363 |             Ok(class)
    |             ^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Err` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/unicode.rs:380:13
    |
380 |             Err(Error::PropertyNotFound)
    |             ^^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Ok` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/unicode.rs:397:9
    |
397 |         Ok(hir_class(PERL_WORD))
    |         ^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Ok` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/unicode.rs:421:9
    |
421 |         Ok(hir_class(WHITE_SPACE))
    |         ^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Ok` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/unicode.rs:445:9
    |
445 |         Ok(hir_class(DECIMAL_NUMBER))
    |         ^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Ok` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/unicode.rs:474:20
    |
474 |             return Ok(true);
    |                    ^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Ok` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/unicode.rs:476:9
    |
476 |         Ok(PERL_WORD
    |         ^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Ok` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/unicode.rs:504:5
    |
504 |     Ok(match normalized_value {
    |     ^^ not found in this scope

error[E0425]: cannot find function, tuple struct or tuple variant `Some` in this scope
   --> /root/.cargo/registry/src/index.crates.io-6f17d22bba15001f/regex-syntax-0.8.5/src/unicode.rs:505:18
    |
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
