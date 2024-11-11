

export function getFpDid({ did }: { did?: string }): string {
  if (!did) {
    return "";
  }
  const fphandleRegex = /(❤️|<3)\s*@(\S+)\s*(❤️|<3)/;
  const match = did.match(fphandleRegex);
  if (match) {
    const loverHandle = match[2];
    return resolveDidForHandle(loverHandle); 
  }
  return "";
}

export function augmentSearchQuery(query: string, { did }: { did?: string }): string {
  if (!did) {
    return query;
  }

  const splits = query.split(/("(?:[^"\\]|\\.)*")/g);

  return splits
    .map((str, idx) => {
      if (idx % 2 === 0) {
        // Replace `from:me` with the actual DID
        str = str.replace(/\bfrom:me\b/g, `${did}`);

        const fpDid = getFpDid({ did });
        if (fpDid) {
          // Replace `from:fp` with the DID of the lover (fpDid)
          str = str.replace(/\bfrom:fp\b/g, `${fpDid}`);
        }
      }
      return str;
    })
    .join('');
}

// Hypothetical API function to resolve handle to DID
function resolveDidForHandle(handle: string): string {
  // Imagine this function makes an API call to resolve the handle to a DID
  return `did:example:${handle}`;
}
